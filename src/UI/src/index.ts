import { serve } from "bun";
import index from "./index.html";

import db from './db/db';

const server = serve({
  routes: {
    // Serve index.html for all unmatched routes.
    "/*": index,

    "/localApi/getConvs": {
      async GET(req) {
        const convs = db.query("SELECT id, name FROM convs").all();
        return new Response(JSON.stringify(convs), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
      },
    },

    "/localApi/getConv/:convId": async req => {
      const id = req.params.convId;
      console.log(id);
      const query = db.query(`SELECT * FROM '${id}'`);
      const conversations = await query.all()
      return new Response(JSON.stringify(conversations), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
    },
    "/api/hello/:name": async req => {
      const name = req.params.name;
      return Response.json({
        message: `Hello, ${name}!`,
      });
    },
  },

  development: process.env.NODE_ENV !== "production" && {
    // Enable browser hot reloading in development
    hmr: true,

    // Echo console logs from the browser to the server
    console: true,
  },
});

console.log(`🚀 Server running at ${server.url}`);
