const axios = require('axios');

async function routeTask(prompt) {
    const meshUrl = process.env.NEONMESH_URL || 'http://neonmesh:8001';
    try {
        const response = await axios.post(`${meshUrl}/router`, { prompt });
        return response.data.route || 'research';
    } catch (e) {
        console.error("Routing error, defaulting to research:", e.message);
        return 'research';
    }
}

module.exports = { routeTask };
