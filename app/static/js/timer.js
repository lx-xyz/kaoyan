(function() {
    var TOTAL_SECONDS = 25 * 60;
    var seconds = TOTAL_SECONDS;
    var isRunning = false;
    var intervalId = null;
    var sessionStart = null;
    var circumference = 722.6; // 2 * PI * 115

    var display = document.getElementById('timer-display');
    var label = document.getElementById('timer-label');
    var ring = document.getElementById('progress-ring');
    var btnStart = document.getElementById('btn-start');
    var btnPause = document.getElementById('btn-pause');
    var btnReset = document.getElementById('btn-reset');
    var subjectSelect = document.getElementById('subject-select');
    var todayMinutesEl = document.getElementById('today-minutes');

    function formatTime(s) {
        var m = Math.floor(s / 60);
        var sec = s % 60;
        return String(m).padStart(2, '0') + ':' + String(sec).padStart(2, '0');
    }

    function updateDisplay() {
        display.textContent = formatTime(seconds);
        var progress = (TOTAL_SECONDS - seconds) / TOTAL_SECONDS;
        ring.style.strokeDashoffset = circumference * progress;
        if (seconds < 60 && isRunning && seconds > 0) {
            ring.style.stroke = '#F44336';
        } else {
            ring.style.stroke = '#4CAF50';
        }
    }

    function startTimer() {
        if (seconds <= 0) return;
        isRunning = true;
        sessionStart = new Date().toISOString();
        btnStart.style.display = 'none';
        btnPause.style.display = '';
        label.textContent = '专注中...';
        intervalId = setInterval(function() {
            seconds--;
            updateDisplay();
            if (seconds <= 0) {
                clearInterval(intervalId);
                isRunning = false;
                btnStart.style.display = '';
                btnPause.style.display = 'none';
                label.textContent = '时间到！';
                ring.style.stroke = '#4CAF50';
                recordSession();
            }
        }, 1000);
    }

    function pauseTimer() {
        clearInterval(intervalId);
        isRunning = false;
        btnStart.style.display = '';
        btnStart.innerHTML = '<i class="bi bi-play-fill me-1"></i>继续';
        btnPause.style.display = 'none';
        label.textContent = '已暂停';
    }

    function resetTimer() {
        clearInterval(intervalId);
        isRunning = false;
        seconds = TOTAL_SECONDS;
        sessionStart = null;
        btnStart.style.display = '';
        btnStart.innerHTML = '<i class="bi bi-play-fill me-1"></i>开始';
        btnPause.style.display = 'none';
        label.textContent = '准备开始';
        ring.style.strokeDashoffset = 0;
        ring.style.stroke = '#4CAF50';
        updateDisplay();
    }

    function recordSession() {
        var duration = Math.round((TOTAL_SECONDS - seconds) / 60);
        if (duration < 1) return;

        var body = JSON.stringify({
            subject_id: subjectSelect.value || null,
            duration_minutes: duration,
            start_time: sessionStart
        });

        fetch('/api/timer/record', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body
        }).then(function(r) { return r.json(); })
          .then(function(data) {
              if (data.today_minutes !== undefined) {
                  todayMinutesEl.textContent = data.today_minutes;
              }
          });
    }

    // 自定义时长
    var hoursInput = document.getElementById('hours-input');
    var minutesInput = document.getElementById('minutes-input');
    var btnApply = document.getElementById('btn-apply');

    function applyDuration() {
        var h = parseInt(hoursInput.value) || 0;
        var m = parseInt(minutesInput.value) || 0;
        if (h === 0 && m === 0) { m = 25; minutesInput.value = 25; }
        TOTAL_SECONDS = h * 3600 + m * 60;
        resetTimer();
    }

    btnApply.addEventListener('click', applyDuration);

    btnStart.addEventListener('click', startTimer);
    btnPause.addEventListener('click', pauseTimer);
    btnReset.addEventListener('click', function() {
        if (isRunning && seconds < TOTAL_SECONDS && confirm('确定要重置计时吗？本次学习记录将丢失。')) {
            resetTimer();
        } else if (!isRunning) {
            resetTimer();
        }
    });

    updateDisplay();
})();
