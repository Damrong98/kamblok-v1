/* 
 * For: Animate Menu and Sidebar
 *
 *
 */
function toggleMenu() {
    let sidebar = document.getElementById("sidebar");
    let contentBody = document.getElementById("contentBody");

    let headerLogo = document.getElementById("logoHeader");

    if (contentBody.classList.contains("show_full_content")) {
        contentBody.classList.remove("show_full_content");
        contentBody.classList.add("show_content");
        // logo
        headerLogo.style.display="none";
        // headerLogo.classList.remove("visible");
        // headerLogo.classList.add("hidden");

    } else {
        contentBody.classList.add("show_full_content");
        contentBody.classList.remove("show_content");
        // logo
        // headerLogo.classList.remove("hidden");
        // headerLogo.classList.add("visible");
        headerLogo.style.display="block";
    }

    if (sidebar.classList.contains("show_sidebar")) {
        sidebar.classList.remove("show_sidebar");
        sidebar.classList.add("hide_sidebar");
        overlay.classList.remove("active");

    } else {
        sidebar.classList.add("show_sidebar");
        sidebar.classList.remove("hide_sidebar");
        overlay.classList.add("active");
    }
}


/* 
 * For: Change Model Api
 *
 *
 */
// Sample model_api data (replace with actual API fetch if needed)
let model_api = [
    { name: "Gemini 2.0 Flash", modelValue: "gemini-2.0-flash", active: true },
    { name: "Gemini 2.0 Flash", modelValue: "gemini-2.0-flash-lite", active: false },
    { name: "Gemini 2.2 Pro Experimental", modelValue: "gemini-2.0-pro-exp-02-05", active: false },
    { name: "Gemini 1.0 Flash", modelValue: "gemini-1.5-flash", active: false },
    // { name: "DeepSeek-R1", modelValue: "deepseek-ai/DeepSeek-R1", active: false },
    // { name: "Quen", modelValue: "Qwen/QwQ-32B", active: false },
];

// Global function to access model_api data
// function globalModelApi() {
// Define globalModelApi and attach it to window
window.globalModelApi = function() {
    return {
        getAll: () => model_api,
        getDescription: (index) => model_api[index]?.modelValue,
        getActiveModel: () => model_api.find(model => model.active === true),
        setActive: (index) => {
            model_api = model_api.map((model, i) => ({
                ...model,
                active: i === parseInt(index)
            }));
            return model_api;
        }
    };
}

// Async function to populate the dropdown
async function populateDropdown() {
    try {
        const dropdownMenu = document.getElementById('dropdownModelApi');
        dropdownMenu.innerHTML = ''; // Clear existing items

        model_api.forEach((model, index) => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <a class="dropdown-item item_api d-flex justify-content-between align-items-center" href="#" data-index="${index}">
                    <div>
                        <strong>${model.name}</strong>
                        <br><small>${model.modelValue}</small>
                    </div>
                    <span class="badge bg-secondary">${model.active ? '✔' : ''}</span>
                </a>
            `;
            dropdownMenu.appendChild(listItem);
        });

        // Add event listeners after populating
        addDropdownListeners();
    } catch (error) {
        console.error('Error populating dropdown:', error);
    }
}

// Function to add click event listeners to dropdown items
function addDropdownListeners() {
    const dropdownItems = document.querySelectorAll('.item_api');
    dropdownItems.forEach(item => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            const index = item.getAttribute('data-index');
            const modelApi = globalModelApi();
            
            // Set the clicked model as active
            modelApi.setActive(index);
            const selectedModel = model_api[index];

            // Update button text and log
            console.log('Selected model:', selectedModel);
            document.getElementById('dropdownToggleAPI').textContent = selectedModel.name;

            // Refresh dropdown to show updated active status
            populateDropdown();
        });
    });
}


document.getElementById('dropdownToggleAPI').textContent = model_api[0].name;
// Populate the dropdown on page load
window.onload = populateDropdown;

// Example usage of globalModelApi:
// const api = globalModelApi();
// console.log(api.getDescription(0)); // "Our model is coming soon.."
// console.log(api.getActiveModel()); // Returns the currently active model
// api.setActive(2); // Sets model at index 2 as active

// Example usage of globalModelApi:
// const api = globalModelApi();
// console.log(api.getActiveModel().modelValue);
