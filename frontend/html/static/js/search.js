document.addEventListener("DOMContentLoaded", function () {
    function updateDetailView(content) {
        facultyDetails = document.getElementById("facultyDetails");
        facultyDetails.innerHTML = content;
        document.getElementById("detailBox").classList.remove("hidden");
    }
    function hideSearch() {
        document.getElementById("searchForm").classList.add("hidden");
        document.getElementById("results").classList.add("hidden");
        document.getElementById("resultsHeading").classList.add("hidden");
    }
    document.getElementById("backToSearch").addEventListener("click", function() {
        document.getElementById("facultyDetails").innerHTML = "";
        document.getElementById("searchForm").classList.remove("hidden");
        document.getElementById("results").classList.remove("hidden");
        document.getElementById("resultsHeading").classList.remove("hidden");
        document.getElementById("detailBox").classList.add("hidden");
    });
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
                
                document.getElementById("resultsHeading").classList.remove("hidden");

                data.results.forEach(item => {
                    // Create a result container div
                    let resultDiv = document.createElement("div");
                    resultDiv.className = "result";

                    // Add Name
                    let nameEl = document.createElement("p");
                    nameEl.innerHTML = `<h3>${item.name}</h3>`;
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

                    // Add button to view details
                    let viewDetailsButton = document.createElement("button");
                    viewDetailsButton.innerHTML = "View Details →";
                    viewDetailsButton.style.marginBottom = "20px";
                    viewDetailsButton.addEventListener("click", function() {
                        hideSearch();
                        updateDetailView(`
                            <h2>${item.name}</h2>
                            <p><strong>School:</strong> ${item.school}</p>
                            <p><strong>Department:</strong> ${item.department}</p>
                            <p><strong>About:</strong> ${item.about}</p>
                            <p><strong>Profile URL:</strong> <a href="${item.profile_url}" target="_blank">${item.profile_url}</a></p>
                        `);
                    });
                    resultDiv.appendChild(viewDetailsButton);

                    // Append the result div to the results container
                    resultsContainer.appendChild(resultDiv);
                });
            })
            .catch(error => console.error("Error fetching data:", error));
    });
});
