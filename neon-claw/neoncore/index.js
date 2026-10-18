const express = require('express');
const { initQueue, taskQueue } = require('./taskQueue');
const eventBus = require('./eventBus');
const { printBanner } = require('./banner');

const app = express();
app.use(express.json());

const port = process.env.PORT || 3000;

app.post('/ask', async (req, res) => {
    const { prompt, userId } = req.body;
    const job = await taskQueue.add('agentTask', { prompt, userId });
    res.json({ jobId: job.id });
});

app.listen(port, () => {
    printBanner("Central Task Orchestrator (Port " + port + ")");
    console.log(`[NeonCore] Task dispatcher ready. Booting BullMQ queues...`);
    initQueue();
});

