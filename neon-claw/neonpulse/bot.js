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

// 6. Natural Language Handler (No /ask needed!)
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

// 7. Reply Worker (Delivers text responses & Obscura screenshots to Phone)
const replyWorker = new Worker('neon-replies', async job => {
    const { userId, resultText, media } = job.data;
    if (bot.telegram) {
        try {
            // 1. Send Rich Media / Screenshots first if present
            if (Array.isArray(media) && media.length > 0) {
                for (const item of media) {
                    if (item.type === 'photo_base64' && item.data) {
                        const buffer = Buffer.from(item.data, 'base64');
                        await bot.telegram.sendPhoto(
                            userId, 
                            { source: buffer }, 
                            { caption: item.caption || "🌐 Obscura Browser Screenshot" }
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

process.once('SIGINT', () => bot.stop && bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop && bot.stop('SIGTERM'));
