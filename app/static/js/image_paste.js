/**
 * 截图粘贴上传 — 绑定到所有带 data-paste-upload 属性的 textarea
 * 用法：<textarea data-paste-upload></textarea>
 * 用户在 textarea 中 Ctrl+V 粘贴截图 → 自动上传 → 插入 ![](url)
 */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('textarea[data-paste-upload]').forEach(function (textarea) {
        var uploadingHint = null;

        // 显示上传中提示
        function showUploading() {
            if (uploadingHint) return;
            uploadingHint = document.createElement('span');
            uploadingHint.textContent = ' 图片上传中...';
            uploadingHint.style.cssText = 'color:#FFA000;font-size:0.85rem;font-weight:bold;';
            uploadingHint.id = 'paste-upload-hint';
            textarea.parentNode.appendChild(uploadingHint);
        }

        function hideUploading() {
            if (uploadingHint) {
                uploadingHint.remove();
                uploadingHint = null;
            }
        }

        textarea.addEventListener('paste', function (e) {
            var items = e.clipboardData && e.clipboardData.items;
            if (!items) return;

            for (var i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') === 0) {
                    e.preventDefault(); // 阻止默认粘贴行为
                    var blob = items[i].getAsFile();
                    uploadImage(blob, textarea);
                    return;
                }
            }
            // 如果不是图片，正常粘贴文本
        });

        function uploadImage(blob, target) {
            showUploading();
            var formData = new FormData();
            formData.append('image', blob, 'screenshot.png');

            fetch('/upload/image', {
                method: 'POST',
                body: formData
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                hideUploading();
                if (data.url) {
                    insertAtCursor(target, '![](' + data.url + ')');
                } else {
                    alert('图片上传失败: ' + (data.error || '未知错误'));
                }
            })
            .catch(function (err) {
                hideUploading();
                alert('图片上传失败: ' + err.message);
            });
        }

        function insertAtCursor(field, text) {
            var start = field.selectionStart;
            var end = field.selectionEnd;
            var before = field.value.substring(0, start);
            var after = field.value.substring(end);
            field.value = before + text + after;
            field.selectionStart = field.selectionEnd = start + text.length;
            field.focus();
        }
    });
});
