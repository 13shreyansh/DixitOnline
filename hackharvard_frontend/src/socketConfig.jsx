import { io } from "socket.io-client"
import { backend_url } from "./backendUrl"

const socket = io(backend_url, {
  transports: ["polling"],
});

export default socket
