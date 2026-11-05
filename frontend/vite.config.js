import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const workspaceRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    fs: { allow: [workspaceRoot] },
  },
});
