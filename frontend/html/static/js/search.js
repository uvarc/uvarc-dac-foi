schoolDepartments = {
    "SOM": ["Cell Biology",
        "Biochemistry and Molecular Genetics",
        "Microbiology, Immunology, Cancer Biology",
        "Molecular Physiology and Biological Physics",
        "Pharmacology"],
    "SEAS": ["Biomedical Engineering",
        "Chemical Engineering",
        "Civil and Environmental Engineering",
        "Computer Engineering",
        "Computer Science",
        "Electrical and Computer Engineering",
        "Engineering and Society",
        "Materials Science and Engineering",
        "Mechanical and Aerospace Engineering",
        "Systems and Information Engineering"],
};

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
    // change the department dropdown's options based on the school dropdown's selection
    document.getElementById("school").addEventListener("change", function() {
        let school = this.value;
        let departmentDropdown = document.getElementById("department");
        departmentDropdown.innerHTML = ""; // Clear previous options

        let blankOption = document.createElement("option");
        blankOption.value = "";
        blankOption.text = "Any";
        departmentDropdown.appendChild(blankOption);

        schoolDepartments[school].forEach(department => {
            let option = document.createElement("option");
            option.value = department;
            option.text = department;
            departmentDropdown.appendChild(option);
        });
        
        departmentDropdown.disabled = !school;
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

        document.getElementById("loadingSpinner").classList.remove("hidden");
        fetch(`/api/search?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                let resultsContainer = document.getElementById("results");
                resultsContainer.innerHTML = ""; // Clear previous results
                
                document.getElementById("resultsHeading").classList.remove("hidden");
                document.getElementById("loadingSpinner").classList.add("hidden");
                data.results.forEach(item => {
                    // Create a result container div
                    let resultDiv = document.createElement("div");
                    resultDiv.className = "result searchResult";

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
                    viewDetailsButton.addEventListener("click", function() {
                        hideSearch();
                        window.scrollTo(0, 0);
                        updateDetailView(`
                            <h2>${item.name}</h2>
                            <p><strong>School:</strong> ${item.school}</p>
                            <p><strong>Department:</strong> ${item.department}</p>
                            <p><strong>About:</strong> ${item.about}</p>
                            <p><strong>Profile URL:</strong> <a href="${item.profile_url}" target="_blank">${item.profile_url}</a></p>
                            <h3>Projects</h3>
                                ${item.projects.map(project => {
                                    let relTerms = project.relevant_terms.split("><");
                                    return `
                                    <div class="result">
                                        <strong>Project Number:</strong> ${project.project_number}<br>
                                        ${
                                        project.abstract.length > 200 
                                            ? `<details class="truncated"><summary><strong>Abstract:</strong> <span>${project.abstract.slice(0, 200)}...</span></summary>${project.abstract}</details>`
                                            : "<strong>Abstract:</strong> " + project.abstract + "<br>"
                                        }
                                            ${relTerms.length < 10 ? "<strong>Relevant Terms:</strong> " + relTerms.join(", ").replace(/(<|>)/g, "") + "<br>": `
                                        <details class="truncated">
                                            <summary><strong>Relevant Terms (${relTerms.length}):</strong> <span>${relTerms.slice(0, 10).join(", ").replace(/(<|>)/g, "")}...</span>
                                            </summary>
                                            ${relTerms.join(", ").replace(/(<|>)/g, "")}
                                        </details>`}
                                        <strong>Dates:</strong> ${new Date(project.start_date).toLocaleDateString("en-US", {year: 'numeric', month: 'long', day: 'numeric'})}
                                         — ${new Date(project.end_date).toLocaleDateString("en-US", {year: 'numeric', month: 'long', day: 'numeric'})}<br>
                                        <strong>Agency IC Admin:</strong> ${project.agency_ic_admin}<br>
                                        <strong>Activity Code:</strong> ${project.activity_code}
                                    </div>`;
                                }).join("")}
                        `);
                    });
                    resultDiv.appendChild(viewDetailsButton);

                    // Append the result div to the results container
                    resultsContainer.appendChild(resultDiv);
                });
            })
            .catch(error => {
                document.getElementById("loadingSpinner").classList.add("hidden");
                return console.error("Error fetching data:", error);
            });
    });
});
