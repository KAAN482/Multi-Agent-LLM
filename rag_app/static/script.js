document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const fileList = document.getElementById('file-list');
    const clearDbBtn = document.getElementById('clear-db-btn');
    const logBody = document.getElementById('log-body');

    function addLog(text, type = 'system') {
        const div = document.createElement('div');
        div.classList.add('log-entry', type);
        div.textContent = `> ${text}`;
        logBody.appendChild(div);
        logBody.scrollTop = logBody.scrollHeight;
    }

    // --- Chat Functions ---

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);

        if (sender === 'bot') {
            // Render Markdown safely
            const dirty = marked.parse(text);
            const clean = DOMPurify.sanitize(dirty);
            msgDiv.innerHTML = clean;
        } else {
            msgDiv.textContent = text;
        }

        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // User message
        addMessage(text, 'user');
        userInput.value = '';

        // Loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'bot');
        loadingDiv.innerHTML = '<i>Düşünüyorum... 🧠</i>';
        loadingDiv.id = 'loading-msg';
        chatContainer.appendChild(loadingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            // SSE (Server-Sent Events) ile Bağlan
            const eventSource = new EventSource(`/api/agent/stream?query=${encodeURIComponent(text)}`);
            let finalAnswerReceived = false;

            eventSource.onmessage = function (event) {
                const data = JSON.parse(event.data);

                // Log alanına yaz (Eğer UI'da varsa, yoksa konsola)
                console.log("SSE Event:", data);

                if (data.event === "node_update") {
                    // Kullanıcıya ara bilgi ver (Opsiyonel: Status bar update)
                    const nodeName = data.node;
                    // loadingDiv içeriğini güncelle
                    loadingDiv.innerHTML = `<i>${nodeName} çalışıyor... ⚙️</i>`;
                    addLog(`${nodeName} tamamlandı.`, 'node');

                    // Eğer içerik varsa ve kullanıcıya göstermek istiyorsak:
                    // addMessage(`[${nodeName}]: ${data.content.substring(0, 100)}...`, 'bot');
                } else if (data.event === "system") {
                    addLog(data.content, 'system');
                } else if (data.event === "final_result") {
                    // Final cevabı göster
                    document.getElementById('loading-msg').remove();
                    addMessage(data.content, 'bot');
                    addLog("Yanıt alındı.", 'system');
                    finalAnswerReceived = true;
                    // Bağlantıyı kapat
                    eventSource.close();
                } else if (data.event === "error") {
                    document.getElementById('loading-msg').remove();
                    addMessage(`❌ Hata: ${data.content}`, 'bot');
                    addLog(`HATA: ${data.content}`, 'error');
                    eventSource.close();
                }
            };

            eventSource.onerror = function (err) {
                console.error("EventSource failed:", err);
                if (!finalAnswerReceived) {
                    // Status: DONE gelmeden koptuysa
                    document.getElementById('loading-msg').remove();
                    addMessage("❌ Bağlantı koptu.", 'bot');
                }
                eventSource.close();
            };

        } catch (err) {
            document.getElementById('loading-msg').remove();
            addMessage(`❌ Bağlantı Hatası: ${err.message}`, 'bot');
        }
    }

    // --- Event Listeners ---

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // --- File Upload Logic ---

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#3b82f6';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#64748b';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#64748b';
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    async function handleFiles(files) {
        if (!files.length) return;

        const formData = new FormData();
        Array.from(files).forEach(file => formData.append('files', file));

        addMessage(`📤 ${files.length} dosya yükleniyor...`, 'bot');

        try {
            const res = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok) {
                addMessage(`✅ ${data.message}`, 'bot');
                loadFiles(); // Refresh list
            } else {
                addMessage(`❌ Yükleme Hatası: ${JSON.stringify(data.errors)}`, 'bot');
            }
        } catch (err) {
            addMessage(`❌ Bağlantı Hatası: ${err.message}`, 'bot');
        }
    }

    async function loadFiles() {
        try {
            const res = await fetch('/files/list');
            const files = await res.json();
            fileList.innerHTML = '';

            files.forEach(file => {
                const item = document.createElement('div');
                item.classList.add('file-item');
                item.textContent = `📄 ${file}`;
                fileList.appendChild(item);
            });
        } catch (err) {
            console.error("Dosya listesi alınamadı:", err);
        }
    }

    clearDbBtn.addEventListener('click', async () => {
        if (confirm("Tüm veritabanını silmek istediğinize emin misiniz?")) {
            try {
                const res = await fetch('/files/clear', { method: 'DELETE' });
                const data = await res.json();
                alert(data.message);
                loadFiles();
            } catch (err) {
                alert("Silme hatası: " + err.message);
            }
        }
    });

    // Initial Load
    loadFiles();
});
