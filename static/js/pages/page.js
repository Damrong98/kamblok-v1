// Add any global JavaScript functionality here
console.log("Script loaded successfully");

// Example: Add a simple click counter
let clickCount = 0;
document.addEventListener('click', function() {
    clickCount++;
    console.log(`Page clicked ${clickCount} times`);
});