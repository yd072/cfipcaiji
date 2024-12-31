// Cloudflare Worker：从 GitHub Pages 读取 ip.txt 文件并显示

async function handleRequest(request) {
    // GitHub Pages URL 或其他存储位置
    const ipFileUrl = 'https://yourusername.github.io/your-repository-name/ip.txt';
    
    // 从 GitHub Pages 获取 ip.txt 文件内容
    const response = await fetch(ipFileUrl);
    
    if (response.ok) {
        const ipText = await response.text();
        return new Response(ipText, {
            headers: {
                'Content-Type': 'text/plain',  // 返回纯文本
                'Cache-Control': 'no-cache',   // 防止缓存
            }
        });
    } else {
        return new Response('无法获取 IP 列表', { status: 500 });
    }
}

// 监听 fetch 事件
addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request));
});
