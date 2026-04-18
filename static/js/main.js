// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const btnConnect = document.getElementById('btn-connect');
    const btnTakeoff = document.getElementById('btn-takeoff');
    const btnLand = document.getElementById('btn-land');
    const btnStartTracking = document.getElementById('btn-start-tracking');
    const btnStopTracking = document.getElementById('btn-stop-tracking');

    const flightStatusText = document.getElementById('flight-status-text');
    const batteryLevelBar = document.getElementById('battery-level-bar');
    const batteryLevelText = document.getElementById('battery-level-text');

    let isConnected = false;
    let isFlying = false;
    let isTracking = false;

    // --- API Communication ---
    async function sendCommand(command) {
        try {
            const response = await fetch(`/api/drone/${command}`, { method: 'POST' });
            const result = await response.json();
            console.log(`Command ${command} status:`, result);
            updateStatus(); // Immediately update status after a command
        } catch (error) {
            console.error(`Error sending command ${command}:`, error);
        }
    }

    async function updateStatus() {
        try {
            const response = await fetch('/api/drone/status');
            const status = await response.json();

            isConnected = status.battery !== 'N/A';
            isFlying = status.is_flying;
            isTracking = status.is_tracking;
            
            updateUI(status);
        } catch (error) {
            console.error('Error fetching status:', error);
            isConnected = false;
            isFlying = false;
            isTracking = false;
            updateUI({battery: "N/A", is_flying: false, is_tracking: false});
        }
    }
    
    // --- UI Update Logic ---
    function updateUI(status) {
        // Update Status Text
        flightStatusText.classList.remove('status-disconnected', 'status-connected', 'status-flying');
        if (status.is_flying) {
            flightStatusText.textContent = 'FLYING';
            flightStatusText.classList.add('status-flying');
        } else if (isConnected) {
            flightStatusText.textContent = 'CONNECTED';
            flightStatusText.classList.add('status-connected');
        } else {
            flightStatusText.textContent = 'DISCONNECTED';
            flightStatusText.classList.add('status-disconnected');
        }

        // Update Battery
        if (status.battery !== 'N/A') {
            batteryLevelText.textContent = `${status.battery}%`;
            batteryLevelBar.style.width = `${status.battery}%`;
            // Change battery bar color based on percentage
            const percentage = status.battery / 100;
            // The gradient is from green (0%) to red (100%), so we move the background position.
            // At 100% battery (good), position should be 0%. At 0% battery (bad), it should be 100%.
            const backgroundPosition = (1 - percentage) * 100;
            batteryLevelBar.style.backgroundPosition = `${backgroundPosition}% 0`;

        } else {
            batteryLevelText.textContent = 'N/A';
            batteryLevelBar.style.width = '0%';
        }
        
        // Update Button States
        btnConnect.textContent = isConnected ? 'Disconnect' : 'Connect';
        
        btnTakeoff.disabled = !isConnected || isFlying;
        btnLand.disabled = !isConnected || !isFlying;
        
        btnStartTracking.disabled = !isFlying || isTracking;
        btnStopTracking.disabled = !isFlying || !isTracking;
    }

    // --- Event Listeners ---
    btnConnect.addEventListener('click', () => {
        const command = isConnected ? 'disconnect' : 'connect';
        sendCommand(command);
    });

    btnTakeoff.addEventListener('click', () => sendCommand('takeoff'));
    btnLand.addEventListener('click', () => sendCommand('land'));
    btnStartTracking.addEventListener('click', () => sendCommand('start_tracking'));
    btnStopTracking.addEventListener('click', () => sendCommand('stop_tracking'));



    // --- Initialization ---
    // Poll for status updates every 3 seconds
    setInterval(updateStatus, 3000);
    // Initial status check
    updateStatus();

    // --- [色彩修复] 新增: 启动前端颜色校正循环 ---
    let animationFrameId;

    function processFrame() {
        // 确保视频源和画布尺寸一致
        if (canvas.width !== videoSource.naturalWidth) {
            canvas.width = videoSource.naturalWidth;
            canvas.height = videoSource.naturalHeight;
        }

        // 1. 将隐藏的 "蓝色" 视频帧画到画布上
        ctx.drawImage(videoSource, 0, 0, canvas.width, canvas.height);

        // 2. 从画布获取像素数据
        // (仅在画布有内容时操作，避免启动时的错误)
        if (canvas.width > 0 && canvas.height > 0) {
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data; // data 是一个一维数组 [R, G, B, A, R, G, B, A, ...]

            // 3. 遍历所有像素，交换 R 和 B 的值
            for (let i = 0; i < data.length; i += 4) {
                const red = data[i];
                const blue = data[i + 2];
                
                data[i] = blue;     // 将原来的蓝色值赋给红色通道
                data[i + 2] = red;  // 将原来的红色值赋给蓝色通道
                // G (data[i+1]) 和 A (data[i+3]) 通道保持不变
            }
            
            // 4. 将修改后的像素数据放回画布
            ctx.putImageData(imageData, 0, 0);
        }
        
        // 5. 请求浏览器在下一次重绘前再次调用此函数，形成流畅视频
        animationFrameId = requestAnimationFrame(processFrame);
    }

    // 当隐藏的img开始加载视频流时，启动处理循环
    videoSource.onload = () => {
        console.log("Video stream source loaded, starting color correction loop.");
        // 如果之前有循环在跑，先停掉
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        processFrame();
    };
    // --- [修复结束] ---

}); // 这是 addEventListener 的结尾括号，确保代码在它之前