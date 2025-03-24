const url = "http://127.0.0.1";
const port = 5000;

async function query(method = "GET", path = "/", body = {}, token = "") {
    try {
        var payload = {
            method: method,
            mode: "cors",
            headers: {},
            credentials: 'include'
        };
        if (token !== "") {
            payload.headers["Authorization"] = `Bearer ${token}`
        }
        if (method !== "GET" && body instanceof FormData) {
            payload.body = body;
        } else if (method !== "GET" && Object.keys(body).length > 0) {
            payload.body = JSON.stringify(body);
            payload.headers['Content-Type'] = 'application/json';
        }
        const final_url = `${url}:${port}${path}`
        const response = await fetch(final_url, payload);

        if (!response.ok) {
            throw new Error(`Error: ${response}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

async function get(path = "/", body = {}, token = "") {
    return await query("GET", path, body, token)
}

async function put(path = "/", body = {}, token = "") {
    return await query("PUT", path, body, token)
}

async function post(path = "/", body = {}, token = "") {
    return await query("POST", path, body, token)
}

async function patch(path = "/", body = {}, token = "") {
    return await query("PATCH", path, body, token)
}

async function delete_query(path = "/", body = {}, token = "") {
    return await query("DELETE", path, body, token)
}

const queries = {
    query,
    get,
    put,
    post,
    patch,
    delete_query
};

export { queries };
