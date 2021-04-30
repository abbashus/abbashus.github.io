console.log("start")

const lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum";

function fetchdata() {
    fetch("https://reqres.in/api/users")
        .then(response => {
            if(!response.ok) {
                throw Error("Some error from api");
            }
            const res = response.json();
            console.log(res);
            return res;
        }).then(results => {
        console.log(results);
        const html = results.data.map(
            user => {
                return `
                    <div class="card border-info my-card " >
                    <h5 class="card-header">${user.first_name}
                        <span class="badge rounded-pill bg-warning text-dark" style="float: right;">DOC</span>
                    </h5>
                    <div class="card-body">                      
                        <h6 class="card-subtitle mb-2 text-muted">${user.email}</h6>
                        <p class="card-text">${lorem}</p>
                    </div>
                    </div>
                    `;
            }
        ).join(" ")
        console.log(html);
        document.querySelector("#results").insertAdjacentHTML("afterbegin", html);
    }).catch(error => {
        console.log(error);
    });
}

function search() {

     const query = document.getElementById("search_input").value;
     const search_body = {
         "query": {
             "match": {
                 "content": {
                     "query": query
                 }
             }
         },
         "_source": [
             "url",
             "version",
             "type",
             "summary"
         ]
     }

    fetch("http://localhost:9200/docs/_search", {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(search_body)

    }).then(response => {
            if(!response.ok) {
                throw Error("Some error from opensearch api");
            }
            const res = response.json()
            return res;
        }).then(results => {
            const hits = results.hits.hits;

            let html = '';

            if(hits.length == 0) {
                html += `
                <div class="alert alert-warning" role="alert">
                  No matches found! :(
                </div>
                `
            } else {
                html = hits.map(
                    hit => {
                        const source = hit._source;
                        return `
                        <div class="card border-info my-card " style="border: 2px solid green;" >
                        <h5 class="card-header">${source.url}
                            <span class="badge rounded-pill bg-warning text-dark" style="float: right;">${source.type}</span>
                        </h5>
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">${source.version}</h6>
                            <p class="card-text">${source.summary}</p>
                        </div>
                        </div>
                    `;

                    }
                ).join(" ");
            }

            console.log(html);
            document.querySelector("#results").innerHTML = html;

    }).catch(error => {
        console.log(error);
    });
}

// https://stackoverflow.com/questions/7060750/detect-the-enter-key-in-a-text-input-field
document.getElementById("search_input").addEventListener('keyup', ({key}) => {
    if (key === "Enter") {
        search();
    }
});

document.getElementById("search_button").onclick = function () {
    search();
};