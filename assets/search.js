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
        document.querySelector("#results").innerHTML += html;
    }).catch(error => {
        console.log(error);
    });
}

fetchdata()