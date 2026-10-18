const EventEmitter = require('events');
class NeonEventBus extends EventEmitter {}
const eventBus = new NeonEventBus();
module.exports = eventBus;
