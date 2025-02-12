document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("searchForm").addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(this)
        const params = new URLSearchParams()

        for (const [key, value] of formData.entries()) {
            if (value) {
                params.append(key, value)
            }
        }

        fetch(`/api/search?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                let resultsContainer = document.getElementById("results");
                resultsContainer.innerHTML = ""; // Clear previous results

                data.results.forEach(item => {
                    // Create a result container div
                    let resultDiv = document.createElement("div");
                    resultDiv.style.marginBottom = "40px"; // Add space between results
                    resultDiv.style.borderBottom = "1px solid #ccc"; // Optional: Add a divider for clarity
                    resultDiv.style.paddingBottom = "20px"; // Add padding within the result container

                    // Add Name
                    let nameEl = document.createElement("p");
                    nameEl.innerHTML = `<strong>Name:</strong> ${item.name}`;
                    resultDiv.appendChild(nameEl);

                    // Add School
                    let schoolEl = document.createElement("p");
                    schoolEl.innerHTML = `<strong>School:</strong> ${item.school}`;
                    resultDiv.appendChild(schoolEl);

                    // Add Department
                    let departmentEl = document.createElement("p");
                    departmentEl.innerHTML = `<strong>Department:</strong> ${item.department}`;
                    resultDiv.appendChild(departmentEl);

                    // Add About (truncate to 300 characters)
                    let aboutEl = document.createElement("p");
                    let truncatedAbout = item.about.length > 1000
                        ? item.about.slice(0, 1000) + "..."
                        : item.about;
                    aboutEl.innerHTML = `<strong>About:</strong> ${truncatedAbout}`;
                    resultDiv.appendChild(aboutEl);

                    // Add Profile URL (as a clickable link)
                    let profileUrlEl = document.createElement("p");
                    profileUrlEl.innerHTML = `<strong>Profile URL:</strong> <a href="${item.profile_url}" target="_blank">${item.profile_url}</a>`;
                    resultDiv.appendChild(profileUrlEl);

                    // Append the result div to the results container
                    resultsContainer.appendChild(resultDiv);
                });
            })
            .catch(error => console.error("Error fetching data:", error));
    });
});
