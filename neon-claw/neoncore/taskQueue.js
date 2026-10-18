const { Queue, Worker } = require('bullmq');
const Redis = require('ioredis');
const { routeTask } = require('./router');
const axios = require('axios');

const redisOptions = {
    host: process.env.REDIS_HOST || 'redis',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    maxRetriesPerRequest: null
};

const connection = new Redis(redisOptions);
const taskQueue = new Queue('neon-tasks', { connection });
const replyQueue = new Queue('neon-replies', { connection });

const ALLOWED_AGENTS = ['hermes', 'research', 'code', 'write', 'analyze', 'primary', 'assistant'];

function initQueue() {
    const worker = new Worker('neon-tasks', async job => {
        const { prompt, userId } = job.data;
        console.log(`[NeonCore] Processing job ${job.id} for user ${userId}`);
        
        // 1. Route task
        let agentType = await routeTask(prompt);
        if (!ALLOWED_AGENTS.includes(agentType)) {
            console.warn(`[NeonCore] Unknown agent type '${agentType}', defaulting to 'hermes'`);
            agentType = 'hermes';
        }
        console.log(`[NeonCore] Routed to agent: ${agentType}`);
        
        // 2. Call specialist agent in neonmesh with timeout
        const meshUrl = process.env.NEONMESH_URL || 'http://neonmesh:8001';
        let resultText = "Error communicating with agent.";
        let media = [];

        try {
            const response = await axios.post(
                `${meshUrl}/agent/${agentType}`, 
                { prompt, user_id: userId },
                { timeout: 35000 }
            );
            resultText = response.data.result || "Task processed.";
            media = response.data.media || [];
        } catch (e) {
            console.error(`[NeonCore] Error calling agent '${agentType}': ${e.message}`);
            resultText = `Execution error: ${e.message}`;
        }
        
        // 3. Save to NeonMem (Shared Vault) with timeout
        const memUrl = process.env.NEONMEM_URL || 'http://neonmem:8002';
        try {
            await axios.post(
                `${memUrl}/remember`, 
                {
                    content: resultText.substring(0, 500),
                    user_id: userId,
                    agent_id: agentType,
                    category: "task_result",
                    tags: ["auto", agentType]
                },
                { timeout: 5000 }
            );
        } catch (e) {
            console.warn(`[NeonCore] Warning: Failed to save to NeonMem: ${e.message}`);
        }

        // 4. Notify NeonPulse reply queue (including any media like screenshots)
        await replyQueue.add('sendReply', { 
            userId, 
            resultText,
            media 
        });

        return { result: resultText, mediaCount: media.length };
    }, { 
        connection,
        concurrency: 5
    });

    worker.on('completed', job => {
        console.log(`[NeonCore] Job ${job.id} completed successfully.`);
    });

    worker.on('failed', (job, err) => {
        console.error(`[NeonCore] Job ${job.id} failed: ${err.message}`);
    });
}

module.exports = { taskQueue, initQueue };
