// stolen from https://elder.dev/posts/open-source-virtual-background/
const tf = require('@tensorflow/tfjs-node-gpu');
const bodyPix = require('@tensorflow-models/body-pix');
const http = require('http');
(async () => {
    const net = await bodyPix.load({
        architecture: 'MobileNetV1',
        outputStride: 16,
        multiplier: 0.75,
        quantBytes: 2,
    });
    const server = http.createServer();
    server.on('request', async (req, res) => {
        var chunks = [];
        req.on('data', (chunk) => {
            chunks.push(chunk);
        });
        req.on('end', async () => {
            image_raw = Buffer.concat(chunks);
            const image = tf.node.decodeJpeg(image_raw);
            segmentation = await net.segmentPerson(image, {
                flipHorizontal: false,
                internalResolution: 'medium',
                segmentationThreshold: 0.7,
            });
            res.writeHead(200, { 'Content-Type': 'application/octet-stream' });
            res.write(Buffer.from(segmentation.data));
            tf.dispose(image);
            
            res.end();
        });
    });
    server.listen(9000);
})();
