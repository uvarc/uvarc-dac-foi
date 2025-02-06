document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("searchForm").addEventListener("submit", function (event) {
        event.preventDefault();

        let query = document.getElementById("query").value;
        let limit = document.getElementById("limit").value;

        fetch(`/search?query=${encodeURIComponent(query)}&limit=${encodeURIComponent(limit)}`)
            .then(response => response.json())
            .then(data => {
                let resultsList = document.getElementById("results");
                resultsList.innerHTML = "";
                data.results.forEach(item => {
                    let li = document.createElement("li");
                    li.textContent = item.name;
                    resultsList.appendChild(li);
                });
            })
            .catch(error => console.error("Error fetching data:", error));
    });
});
