// 在整个HTML文档加载并解析完毕后，添加一个事件监听器来监听DOMContentLoaded事件。
document.addEventListener('DOMContentLoaded', function() {
    // 在DOM完全加载后立即调用fetchStatus函数。
    fetchStatus();

    // 定义fetchStatus函数，用于从服务器获取状态数据。
    function fetchStatus() {
        // 使用Fetch API向服务器的 /api/status 端点发出GET请求。
        fetch('http://10.223.44.77:5000/api/status')
            // 当服务器响应时，将响应转换为JSON格式。
            .then(response => response.json())
            // 然后将数据传递给更新表格的函数。
            .then(data => {
                // 更新测试平台表格。
                updateTestBenchTable(data);
                // 更新资源使用情况表格。
                updateResourceUsageTable(data);
                // 更新Docker使用情况表格。
                updateDockerUsageTable(data);
            })
            // 如果获取状态数据失败，打印错误信息到控制台。
            .catch(error => console.error('Failed to fetch status:', error));
    }

    // 定义updateTestBenchTable函数，用于更新测试平台表格。
    function updateTestBenchTable(data) {
        // 获取测试平台表格的tbody元素。
        const tbody = document.getElementById('testBenchTable').getElementsByTagName('tbody')[0];
        // console.log("test")
        // console.log(tbody);
        // console.log("test")

        // 清空表格的现有行。
        tbody.innerHTML = '';
        // 初始化序号。
        let number = 1;

        // 遍历数据中的每个键值对。
        for (const [key, info] of Object.entries(data)) {
            // 如果键以'w'结尾。
            if (key.endsWith('w')) {
                if(info.status == "Available"){
                    // 插入新的一行。
                    const row = tbody.insertRow();
                    // 在新行的第一个单元格中插入序号。
                    row.insertCell(0).textContent = number++;
                    // 在新行的第二个单元格中插入键。
                    row.insertCell(1).textContent = key;
                    // 在新行的第三个单元格中插入用户信息，如果没有用户信息则显示'N/A'。
                    row.insertCell(2).textContent = info.users_info || 'N/A';

                    const bookCell = row.insertCell(3);
                    const bookButton = document.createElement('button');
                    bookButton.textContent = '预约';
                    bookButton.className = 'book-button';
                    bookButton.onclick = () => {
                        window.location.href = `../static/book.html?server_id=${key}`;
                    };
                    bookCell.appendChild(bookButton);
                }
                else{
                    // 插入新的一行。
                    const row = tbody.insertRow();
                    // 在新行的第一个单元格中插入序号。
                    row.insertCell(0).textContent = number++;
                    // 在新行的第二个单元格中插入键。
                    row.insertCell(1).textContent = key;
                    // 在新行的第三个单元格中插入用户信息，如果没有用户信息则显示'N/A'。
                    const cell = row.insertCell(3);
                    cell.textContent = "Unavailable";
                    cell.classList.add('unavailable-cell'); // 添加居中显示的CSS类
                    row.classList.add('unavailable-row'); // 添加整行标红的CSS类
                }
            }
        }
    }

    // 定义updateResourceUsageTable函数，用于更新资源使用情况表格。
    function updateResourceUsageTable(data) {
        // 获取资源使用情况表格的tbody元素。
        const tbody = document.getElementById('resourceUsageTable').getElementsByTagName('tbody')[0];
        // 清空表格的现有行。
        tbody.innerHTML = '';
        // 初始化序号。
        let number = 1;

        // 遍历数据中的每个键值对。
        for (const [key, info] of Object.entries(data)) {
            // 如果键以'u'结尾。
            if (key.endsWith('u')) {
                if(info.status == "Available"){
                    // 插入新的一行。
                    const row = tbody.insertRow();
                    // 在新行的第一个单元格中插入序号。
                    row.insertCell(0).textContent = number++;
                    // 在新行的第二个单元格中插入键。
                    row.insertCell(1).textContent = key;
                    // 在新行的后续单元格中插入CPU、RAM和其他资源使用情况，如果没有相关信息则显示'N/A'。
                    row.insertCell(2).textContent = info.cpu || 'N/A';
                    row.insertCell(3).textContent = info.ram || 'N/A';
                    row.insertCell(4).textContent = info.root || 'N/A';
                    row.insertCell(5).textContent = info.data1 || 'N/A';
                    row.insertCell(6).textContent = info.data2 || 'N/A';
                    row.insertCell(7).textContent = info.data3 || 'N/A';
                    row.insertCell(8).textContent = info.data4 || 'N/A';
                }
                else{
                    // 插入新的一行。
                    const row = tbody.insertRow();
                    // 在新行的第一个单元格中插入序号。
                    row.insertCell(0).textContent = number++;
                    // 在新行的第二个单元格中插入键。
                    row.insertCell(1).textContent = key;
                    const cell = row.insertCell(2);
                    cell.textContent = "Unavailable";
                    cell.colSpan = 7; // 合并后面的7个单元格
                    cell.classList.add('unavailable-cell'); // 添加居中显示的CSS类
                    row.classList.add('unavailable-row'); // 添加整行标红的CSS类
                }
                
            }
        }
    }

    // 定义updateDockerUsageTable函数，用于更新Docker使用情况表格。
    function updateDockerUsageTable(data) {
        // 获取 Docker 使用情况表格的 tbody 元素
        const tbody = document.getElementById('dockerUsageTable').getElementsByTagName('tbody')[0];
        // 清空表格的现有行
        tbody.innerHTML = '';
        // 初始化序号
        let number = 1;
    
        // 遍历数据中的每个键值对
        for (const [key, info] of Object.entries(data)) {
            // 如果键以 'u' 结尾
            if (key.endsWith('u')) {
                if(info.status == "Available"){
                    // 获取 Docker 信息并按行拆分
                    const dockerIds = info.docker_id.trim().split('\n');
                    const dockerImages = info.docker_image.trim().split('\n');
                    const dockerStatuses = info.docker_status.trim().split('\n');
        
                    // 插入第一行，显示序号和键值，并合并单元格
                    const row = tbody.insertRow();
                    row.classList.add('highlight-row'); // 添加高亮样式
                    row.insertCell(0).textContent = number++;
                    row.insertCell(1).textContent = key;
                    const cell = row.insertCell(2);
                    cell.textContent = "Available"
                    cell.classList.add('unavailable-cell'); // 添加居中显示的CSS类
                    cell.colSpan = 3;

                    

        
                    // 插入剩余的行，只显示 Docker 信息
                    // 因为新行是空的，所以插入索引 0、1、2 分别对应表格的第三列、第四列和第五列。
                    for (let i = 0; i < dockerIds.length; i++) {
                        const dockerRow = tbody.insertRow();
                        dockerRow.insertCell(0).textContent = "";
                        dockerRow.insertCell(1).textContent = "";
                        dockerRow.insertCell(2).textContent = dockerIds[i];
                        dockerRow.insertCell(3).textContent = dockerImages[i];
                        dockerRow.insertCell(4).textContent = dockerStatuses[i];
                    }
                    
                }
                else{
                    // 插入新的一行。
                    const row = tbody.insertRow();
                    // 在新行的第一个单元格中插入序号。
                    row.insertCell(0).textContent = number++;
                    // 在新行的第二个单元格中插入键。
                    row.insertCell(1).textContent = key;
                    cell = row.insertCell(2)
                    cell.textContent = "Unavailable";
                    cell.colSpan = 3; // 合并后面的7个单元格
                    cell.classList.add('unavailable-cell'); // 添加居中显示的CSS类
                    row.classList.add('unavailable-row'); // 添加整行标红的CSS类
                }
                
            }
        }
    }

    // 设置一个定时器，每10秒钟调用一次fetchStatus函数来刷新数据。
    setInterval(fetchStatus, 10000); // 每10秒刷新一次
});
