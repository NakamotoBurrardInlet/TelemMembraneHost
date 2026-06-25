// client.js
const net = require('net');

const HOST = '127.0.0.1';
const PORT = 9999;

const socket = new net.Socket();
let loggingInterval = null;

socket.connect(PORT, HOST, () => {
    console.log(`[Connected] Secure connection established across membrane to ${HOST}:${PORT}`);
    
    let logicalSequence = 0;
    
    // Continuous Output-Input Data Pipelining Loop
    loggingInterval = setInterval(() => {
        logicalSequence++;
        
        const telemetryFrame = {
            sequence_id: logicalSequence,
            constellation_target: "OMEGA_BETA_NODE",
            sensor_delta: parseFloat((Math.random() * 50).toFixed(4)),
            system_epoch: Date.now()
        };
        
        // Ensure framing safety by applying newline delimiter configuration
        socket.write(JSON.stringify(telemetryFrame) + '\n');
        console.log(`[Output Dispatched] Telemetry Frame Matrix #${logicalSequence}`);
    }, 800); // Sends telemetry every 800ms
});

// Stream Chunk Buffer Processing System
let networkBuffer = '';

socket.on('data', (chunk) => {
    networkBuffer += chunk.toString();
    let boundaryIndex = networkBuffer.indexOf('\n');
    
    // Extract complete structured frames from stream chunks
    while (boundaryIndex !== -1) {
        const structuralFrame = networkBuffer.substring(0, boundaryIndex);
        networkBuffer = networkBuffer.substring(boundaryIndex + 1);
        
        try {
            const analyticalResponse = JSON.parse(structuralFrame);
            if (analyticalResponse.event === "METRIC_ALIGNMENT") {
                console.log("[Input Processed Successfully]:", analyticalResponse.payload);
            }
        } catch (err) {
            console.error("[Membrane Decode Error] Parsing violation:", err.message);
        }
        
        boundaryIndex = networkBuffer.indexOf('\n');
    }
});

socket.on('close', () => {
    console.log('[Disconnected] Network state separated from the main membrane framework.');
    clearInterval(loggingInterval);
});

socket.on('error', (err) => {
    console.error('[Membrane Socket Fault]:', err.message);
});
  
