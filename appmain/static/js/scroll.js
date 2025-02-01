document.addEventListener('DOMContentLoaded', function() {
    const sidebarContainer = document.querySelector('.sidebar-container');
    const sidebar = document.querySelector('.sidebar');

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const offsetHeight = document.documentElement.scrollHeight;
        const innerHeight = window.innerHeight;
        const sidebarHeight = sidebar.offsetHeight;

        if (scrollTop + innerHeight >= offsetHeight - sidebarHeight - 100) {
            sidebarContainer.style.position = 'absolute';
            sidebarContainer.style.top = `${offsetHeight - sidebarHeight}px`;
        } else {
            sidebarContainer.style.position = 'fixed';
            sidebarContainer.style.top = '100px';
            sidebarContainer.style.right = '0px';
            sidebarContainer.style.bottom = '100px';
        }
    });
});