const express = require('express')
const app = express()
const port = 3000
const fs = require('fs');
const path = require('path');
const ffmpeg = require('fluent-ffmpeg');
const videoDir = path.join(__dirname, '..', 'files', 'output');
const thumbnailDir = path.join(__dirname, '..', 'files','thumbnails');

app.use(express.static(__dirname + "/public", {index: false}));


app.get("/", function (request, response) {

	response.sendFile("public/index.html", { root: __dirname });

	//response.sendFile("public/index.html", { root: __dirname });
});

app.get('/videos', (req, res) => {
	
    fs.readdir(videoDir, (err, files) => {
        if (err) {
			console.log(err);
            return res.status(500).json({ error: 'Unable to scan directory' });
        }

        // Filter for mp4 files
        const mp4Files = files.filter(file => path.extname(file).toLowerCase() === '.mp4');
        const promises = mp4Files.map(file => {
            const filePath = path.join(videoDir, file);
            const thumbnailPath = path.join(thumbnailDir, path.basename(file, '.mp4') + '.png');
            const thumbnailUrl = `/thumbnails/${path.basename(file, '.mp4')}.png`;

            return new Promise((resolve, reject) => {
                ffmpeg(filePath)
                    .on('end', () => {
                        console.log(`Thumbnail created for ${file}`);
                        resolve({
                            filename: file,
                            thumbnail: thumbnailUrl
                        });
                    })
                    .on('error', (err) => {
                        console.error(`Error creating thumbnail for ${file}: ${err}`);
                        reject(err);
                    })
                    .screenshots({
                        count: 1,
                        folder: thumbnailDir,
                        size: '320x320',
                        filename: path.basename(file, '.mp4') + '.png'
                    });
            });
        });

        Promise.all(promises)
            .then(results => {
                res.json(results);
            })
            .catch(err => {
                res.status(500).json({ error: 'Error generating thumbnails' });
            });
    });
});

// Serve thumbnails from the thumbnail directory
app.use('/thumbnails', express.static(thumbnailDir));
app.use('/files/output', express.static(videoDir));


app.listen(port, () => {
	console.log(`Example app listening on port ${port}`)
})