/**
 * 首次使用引导 — 多步骤指引
 * 存 localStorage，完成一次后不再显示
 */
(function() {
    // 游客每次都显示，注册用户只显示一次
    var uid = document.querySelector('meta[name="user-id"]');
    var userId = uid ? uid.content : '';
    if (userId && localStorage.getItem('onboarding_done_' + userId) === '1') return;

    var steps = [
        {
            title: '录入题目',
            desc: '将重点题、错题手动录入，支持数学公式和截图粘贴。',
            icon: 'bi-plus-square',
            color: '#E8A817',
            highlight: null,
        },
        {
            title: '做题练习',
            desc: '逐题刷题，自动判断对错。做错的题会自动进入错题本。',
            icon: 'bi-pencil-square',
            color: '#E8A817',
            highlight: null,
        },
        {
            title: '错题追踪',
            desc: '做错的题目自动收集，根据艾宾浩斯记忆曲线安排复习计划。',
            icon: 'bi-exclamation-triangle',
            color: '#D1524A',
            highlight: null,
        },
        {
            title: '单词记忆',
            desc: '添加单词 → 学新词 → 选择题复习。不认识会自动重学。',
            icon: 'bi-book',
            color: '#4A8FC8',
            highlight: null,
        },
        {
            title: '专注计时',
            desc: '番茄钟计时器，记录每天学习时长，可关联科目。',
            icon: 'bi-alarm',
            color: '#5B9A5A',
            highlight: null,
        },
        {
            title: '笔记记录',
            desc: '富文本编辑器，写学习笔记、公式总结，支持直接粘贴图片。',
            icon: 'bi-journal-text',
            color: '#E8734A',
            highlight: null,
        },
        {
            title: '系统设置',
            desc: '设置仪表盘和计时页的背景图片（可上传多张切换），管理你的考试科目。',
            icon: 'bi-gear',
            color: '#E8A817',
            highlight: null,
        },
        {
            title: '批量导入',
            desc: '粘贴题目文本自动解析，或下载Excel模板批量导入。',
            icon: 'bi-upload',
            color: '#D4688A',
            highlight: null,
        },
    ];

    var current = 0;

    // 创建遮罩
    var overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';

    // 创建卡片
    var card = document.createElement('div');
    card.style.cssText = 'background:#fff;border-radius:20px;padding:2rem;max-width:380px;width:90%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.3);animation:fadeInUp 0.4s ease;';

    function render() {
        var s = steps[current];
        var isLast = current === steps.length - 1;
        var dots = steps.map(function(_, i) {
            return '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;margin:0 3px;background:' + (i===current ? s.color : '#ddd') + ';"></span>';
        }).join('');

        card.innerHTML =
            '<div style="font-size:2.5rem;color:'+s.color+';margin-bottom:0.5rem;"><i class="bi '+s.icon+'"></i></div>' +
            '<h5 style="font-weight:700;margin-bottom:0.3rem;">'+s.title+'</h5>' +
            '<p style="color:#6B6B6B;font-size:0.9rem;margin-bottom:1rem;">'+s.desc+'</p>' +
            '<div style="margin-bottom:1rem;">'+dots+'</div>' +
            '<div style="display:flex;gap:0.5rem;justify-content:center;">' +
                (current > 0 ? '<button class="btn btn-outline-secondary btn-sm" onclick="window._onboardPrev()">上一步</button>' : '') +
                '<button class="btn btn-sm" style="background:'+s.color+';color:#fff;border:none;" onclick="window._onboardNext()">' + (isLast ? '开始使用 🚀' : '下一步') + '</button>' +
                '<button class="btn btn-outline-secondary btn-sm" onclick="window._onboardSkip()">跳过</button>' +
            '</div>';
    }

    window._onboardNext = function() {
        if (current < steps.length - 1) {
            current++;
            render();
        } else {
            finish();
        }
    };
    window._onboardPrev = function() {
        if (current > 0) { current--; render(); }
    };
    window._onboardSkip = function() { finish(); };

    function finish() {
        localStorage.setItem('onboarding_done_' + userId, '1');
        document.body.removeChild(overlay);
    }

    overlay.appendChild(card);
    render();
    document.body.appendChild(overlay);
})();
