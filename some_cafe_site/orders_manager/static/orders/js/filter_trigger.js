let typingTimer;

function submitFilterForm() {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
        document.getElementById("order_filter").submit();
    }, 500);
}