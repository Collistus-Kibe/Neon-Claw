require('dotenv').config();
const { Telegraf } = require('telegraf');
const axios = require('axios');
const fs = require('fs');
const { formatResponse } = require('./formatter');
const { Queue, Worker } = require('bullmq');
const Redis = require('ioredis');

const token = process.env.TELEGRAM_BOT_TOKEN;
const rawAllowedUsers = process.env.ALLOWED_TELEGRAM_USER_IDS || "";
const allowedUserIds = rawAllowedUsers ? rawAllowedUsers.split(',').map(s => s.trim()) : [];

let bot;
if (token && token !== "your_telegram_bot_token_here") {
    bot = new Telegraf(token);
} else {
    console.warn("TELEGRAM_BOT_TOKEN not set or is placeholder. Bot polling disabled, worker stays alive.");
    bot = {
        start: () => {},
        command: () => {},
        on: () => {},
        launch: () => {}
    };
    setInterval(() => {}, 1000 * 60 * 60);
}

// User Authorization Guard (Personal AI Privacy)
function isUserAuthorized(ctx) {
    if (!allowedUserIds.length) return true; // If no whitelist configured, allow (open dev mode)
    const senderId = ctx.from && ctx.from.id ? ctx.from.id.toString() : "";
    return allowedUserIds.includes(senderId);
}

const redisOptions = {
    host: process.env.REDIS_HOST || 'redis',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    maxRetriesPerRequest: null
};
const connection = new Redis(redisOptions);
const taskQueue = new Queue('neon-tasks', { connection });

// 1. /start Command
bot.start((ctx) => {
    if (!isUserAuthorized(ctx)) {
        return ctx.reply("⛔ Unauthorized. NemoClaw is a private personal AI system.");
    }
    let mode = "unknown";
    try {
        if (fs.existsSync('/shared/neon_mode.txt')) {
            mode = fs.readFileSync('/shared/neon_mode.txt', 'utf8').trim();
        }
    } catch(e) {}
    ctx.reply(
        `🦁 **NemoClaw Online**\n` +
        `Personal AI System running on Home Server Mesh.\n` +
        `• Model: NVIDIA Nemotron (Nebius Serverless)\n` +
        `• Cognitive Core: Hermes Agent\n` +
        `• Network Mode: [${mode}]\n\n` +
        `💬 *Just talk to me naturally or ask me to browse websites, code, or execute tasks.*`
    );
});

// 2. /mode Command
bot.command('mode', (ctx) => {
    if (!isUserAuthorized(ctx)) return;
    let mode = "unknown";
    try {
        if (fs.existsSync('/shared/neon_mode.txt')) {
            mode = fs.readFileSync('/shared/neon_mode.txt', 'utf8').trim();
        }
    } catch(e) {}
    ctx.reply(`Network Mode: [${mode}]`);
});

// 3. /memory Command
bot.command('memory', async (ctx) => {
    if (!isUserAuthorized(ctx)) return;
    try {
        const memUrl = process.env.NEONMEM_URL || 'http://neonmem:8002';
        const response = await axios.post(`${memUrl}/recall`, { 
            query: "all", 
            user_id: ctx.from.id.toString() 
        }, { timeout: 5000 });
        const count = Array.isArray(response.data) ? response.data.length : 0;
        ctx.reply(`🧠 Shared Memory Vault: [${count} memories stored]`);
    } catch(e) {
        ctx.reply("Error fetching memory entries.");
    }
});

// 4. /skills Command (Lists Reusable Learned Skills)
bot.command('skills', async (ctx) => {
    if (!isUserAuthorized(ctx)) return;
    try {
        const memUrl = process.env.NEONMEM_URL || 'http://neonmem:8002';
        const response = await axios.get(`${memUrl}/skills`, { timeout: 5000 });
        const skills = response.data;
        if (Array.isArray(skills) && skills.length > 0) {
            const list = skills.map(s => `• **${s.name}**: ${s.description}`).join('\n');
            ctx.reply(`🛠️ **Learned Reusable Skills**:\n${list}`);
        } else {
            ctx.reply("🛠️ No learned skills in Shared Vault yet. As Hermes Agent solves repeatable tasks, skills will appear here.");
        }
    } catch(e) {
        ctx.reply("Error fetching skills from vault.");
    }
});

// 5. /status Command (Live Health Check)
bot.command('status', async (ctx) => {
    if (!isUserAuthorized(ctx)) return;
    const checks = [];
    const checkService = async (name, url) => {
        try {
            await axios.get(url, { timeout: 2000 });
            return `✅ ${name}: Online`;
        } catch(e) {
            return `⚠️ ${name}: Unreachable (${e.message})`;
        }
    };

    checks.push(await checkService("Obscura Browser", "http://obscura:8004/health"));
    checks.push(await checkService("NeonMem API", "http://neonmem:8002/docs"));
    checks.push(await checkService("NeonMesh Engine", "http://neonmesh:8001/docs"));

    ctx.reply(`🩺 **NemoClaw Mesh Status**:\n` + checks.join('\n'));
});

// 6. /briefing Command (Autonomous Morning Briefing on demand)
bot.command('briefing', async (ctx) => {
    if (!isUserAuthorized(ctx)) return;
    const userId = ctx.from.id.toString();
    try {
        await ctx.sendChatAction('typing');
    } catch(e) {}
    ctx.reply("🦁 Compiling your Autonomous Executive Morning Briefing (Email Triage + Mesh Telemetry + Tech Radar)...");
    await taskQueue.add('agentTask', { prompt: "generate executive morning briefing", userId });
});

// 7. Natural Language Handler (No /ask needed!)
bot.on('text', async (ctx) => {
    if (!isUserAuthorized(ctx)) {
        return ctx.reply("⛔ Access Denied. Your Telegram ID is not authorized.");
    }
    const text = ctx.message.text.trim();
    if (text.startsWith('/')) return; // Allow Telegraf to handle other commands

    const userId = ctx.from.id.toString();
    try {
        await ctx.sendChatAction('typing');
    } catch(e) {}

    await taskQueue.add('agentTask', { prompt: text, userId });
    ctx.reply("🦁 Processing with NVIDIA Nemotron & Hermes...");
});

// 8. Voice & Speech Ingestion Handler (.ogg / Opus Telegram Voice Notes)
bot.on(['voice', 'audio'], async (ctx) => {
    if (!isUserAuthorized(ctx)) {
        return ctx.reply("⛔ Access Denied. Your Telegram ID is not authorized.");
    }
    const userId = ctx.from.id.toString();
    try {
        await ctx.sendChatAction('record_voice');
    } catch(e) {}

    try {
        const voiceObj = ctx.message.voice || ctx.message.audio;
        const fileId = voiceObj.file_id;
        const fileLink = await ctx.telegram.getFileLink(fileId);
        
        // Fetch audio stream
        const audioResp = await axios.get(fileLink.href, { responseType: 'arraybuffer', timeout: 15000 });
        const audioBase64 = Buffer.from(audioResp.data).toString('base64');
        
        // Send to NeonMesh for Whisper STT transcription
        const meshUrl = process.env.NEONMESH_URL || 'http://neonmesh:8001';
        let transcribedText = "";
        try {
            const tr = await axios.post(`${meshUrl}/voice/transcribe`, {
                audio_base64: audioBase64,
                filename: 'voice.ogg'
            }, { timeout: 15000 });
            transcribedText = tr.data && tr.data.text ? tr.data.text.trim() : "";
        } catch(trErr) {
            console.error("[NeonPulse] Whisper transcription error:", trErr.message);
        }

        if (!transcribedText) {
            transcribedText = "Triage my inbox and give me a briefing";
        }

        ctx.reply(`🎙️ "*${transcribedText}*"\n\n🦁 Dispatching speech prompt to Nemotron & Hermes...`);
        await taskQueue.add('agentTask', { prompt: transcribedText, userId, isVoice: true });
    } catch(err) {
        console.error("[NeonPulse] Failed to process voice note:", err.message);
        ctx.reply("⚠️ Could not process voice note. Falling back to text mode.");
    }
});

// 9. Reply Worker (Delivers text responses, Obscura screenshots, and Voice Notes to Phone)
const replyWorker = new Worker('neon-replies', async job => {
    const { userId, resultText, media } = job.data;
    if (bot.telegram) {
        try {
            // 1. Send Rich Media / Screenshots / Voice first if present
            if (Array.isArray(media) && media.length > 0) {
                for (const item of media) {
                    if (item.type === 'photo_base64' && item.data) {
                        const buffer = Buffer.from(item.data, 'base64');
                        await bot.telegram.sendPhoto(
                            userId, 
                            { source: buffer }, 
                            { caption: item.caption || "🌐 Obscura Browser Screenshot" }
                        );
                    } else if ((item.type === 'voice_base64' || item.type === 'audio_base64') && item.data) {
                        const buffer = Buffer.from(item.data, 'base64');
                        await bot.telegram.sendVoice(
                            userId,
                            { source: buffer },
                            { caption: item.caption || "🎙️ NemoClaw Audio Response" }
                        );
                    }
                }
            }
            // 2. Send Formatted Text Response
            await bot.telegram.sendMessage(userId, formatResponse(resultText));
        } catch(e) {
            console.error(`[NeonPulse] Failed to deliver reply to user ${userId}: ${e.message}`);
        }
    } else {
        console.log(`[NeonPulse Worker] Reply to ${userId}: ${resultText}`);
    }
}, { connection });

const { printBanner } = require('./banner');

if (token && token !== "your_telegram_bot_token_here") {
    printBanner("Telegram Mobile Gateway", "Listening for chats & voice notes");
    bot.launch();
    console.log("[NeonPulse] Connected to Telegram Bot API.");
} else {
    printBanner("Telegram Gateway (Mock Mode)", "Worker active, polling disabled");
}

// 8. Autonomous Proactive Morning Briefing Cron Scheduler
const BRIEFING_ENABLED = process.env.BRIEFING_ENABLED !== 'false';
const BRIEFING_CRON_HOUR = parseInt(process.env.BRIEFING_CRON_HOUR || '8', 10);
let lastBriefingDate = "";

function initAutonomousBriefingScheduler() {
    if (!BRIEFING_ENABLED) {
        console.log("[NeonPulse] Autonomous Morning Briefing scheduler disabled.");
        return;
    }
    console.log(`[NeonPulse] Autonomous Morning Briefing scheduler active (Daily at ${BRIEFING_CRON_HOUR}:00).`);

    setInterval(async () => {
        try {
            const now = new Date();
            const currentHour = now.getHours();
            const todayStr = now.toISOString().slice(0, 10);

            // Fire once per day when clock matches BRIEFING_CRON_HOUR
            if (currentHour === BRIEFING_CRON_HOUR && lastBriefingDate !== todayStr) {
                lastBriefingDate = todayStr;
                console.log(`[NeonPulse] 🦁 Triggering autonomous morning briefing for ${todayStr}...`);

                const recipients = allowedUserIds.length > 0 ? allowedUserIds : [];
                for (const uid of recipients) {
                    await taskQueue.add('agentTask', {
                        prompt: "generate executive morning briefing",
                        userId: uid
                    });
                }
            }
        } catch (err) {
            console.error("[NeonPulse] Briefing scheduler error:", err.message);
        }
    }, 60 * 1000);
}

initAutonomousBriefingScheduler();

process.once('SIGINT', () => bot.stop && bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop && bot.stop('SIGTERM'));
