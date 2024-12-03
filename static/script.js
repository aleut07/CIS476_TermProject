// Clipboard auto-clear after X seconds
function copyToClipboard(text, duration = 5000) {
    navigator.clipboard.writeText(text).then(() => {
        alert("Copied to clipboard. Clipboard will clear in " + (duration / 1000) + " seconds.");
        setTimeout(() => {
            navigator.clipboard.writeText(""); // Clear clipboard
        }, duration);
    }).catch(err => {
        console.error("Could not copy to clipboard", err);
    });
}

// Toggle mask/unmask sensitive data
function toggleMask(elementId) {
    const element = document.getElementById(elementId);
    const isMasked = element.type === "password";
    element.type = isMasked ? "text" : "password";
}

// Auto-lock logic (logout after inactivity)
let autoLockTimeout;

function resetAutoLockTimer(logoutUrl, lockTime = 300000) { // 5 minutes default
    clearTimeout(autoLockTimeout);
    autoLockTimeout = setTimeout(() => {
        window.location.href = logoutUrl; // Redirect to logout
    }, lockTime);
}

// Initialize event listeners for forms or interactions
document.addEventListener("DOMContentLoaded", () => {
    const autoLockTime = 300000; // 5 minutes
    const logoutUrl = "/logout";

    // Reset timer on user activity
    document.body.addEventListener("mousemove", () => resetAutoLockTimer(logoutUrl, autoLockTime));
    document.body.addEventListener("keydown", () => resetAutoLockTimer(logoutUrl, autoLockTime));
    resetAutoLockTimer(logoutUrl, autoLockTime); // Initial timer setup
});
