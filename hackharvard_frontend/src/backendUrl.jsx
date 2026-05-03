const local_backend_url = "http://" + window.location.hostname + ":5001/";
const same_origin_backend_url = window.location.origin + "/";

export const backend_url =
  import.meta.env.VITE_BACKEND_URL ||
  (window.location.port && window.location.port !== "5001"
    ? local_backend_url
    : same_origin_backend_url);
