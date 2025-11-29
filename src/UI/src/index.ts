import { serve } from "bun";
import index from "./index.html";

import db from './db/db';

const randomLetters = (len = 6) => {
  let s = "";
  const alphabet = "abcdefghijklmnopqrstuvwxyz";
  for (let i = 0; i < len; i++) s += alphabet[Math.floor(Math.random() * alphabet.length)];
  return s;
}

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
      const query = db.query(`SELECT * FROM '${id}'`);
      const conversations = await query.all()
      return new Response(JSON.stringify(conversations), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
    },
    '/localApi/createNewConv': {
      async POST(req){
        const randomName = randomLetters(6);
        const smallBlob = new Uint8Array([1, 2, 3]);

        try {
  // start transaction
  db.run("BEGIN");

  // insert into convs
  db.run(
    "INSERT INTO convs (name, blobImg) VALUES (?, ?)",
    [randomName,
    smallBlob]
  );
  const last = db.query("SELECT last_insert_rowid() AS id").all() as {id: number}[];
  const newId = last[0]?.id;
  if (typeof newId !== "number") throw new Error("Failed to obtain last_insert_rowid()");

  // build and safely quote table name: {id}-{randomName}
  const tableName = `${newId}-${randomName}`;
  const quoted = `"${tableName.replace(/"/g, '""')}"`;

  // create the per-conversation table
  db.run(`
    CREATE TABLE ${quoted} (
      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      sender TEXT NOT NULL,
      content TEXT NOT NULL
    )
  `);
  db.run("COMMIT");

  return new Response(
          JSON.stringify({newId: quoted}),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
} catch (err) {
  // rollback on error
  try { db.run("ROLLBACK"); } catch (err) {console.log(err)}
  return new Response(
    JSON.stringify({ error: `DB transaction failed: ${err}` }),
    { status: 500, headers: { "Content-Type": "application/json" } }
  );
}
      }
    },
    '/localApi/saveConvToDb': {
      async POST(req) {
        const {assistantMess, userMess, baseId} = await req.json();
        console.log(assistantMess, userMess, baseId)

        const safeIdentifier = `"${baseId.replace(/"/g, '""')}"`;
        console.log(safeIdentifier)
        try {
        db.run("BEGIN");
        db.run(
          `INSERT INTO ${safeIdentifier} (sender, content) VALUES (?, ?)`,
          "user",
          userMess
        );
        db.run(
          `INSERT INTO ${safeIdentifier} (sender, content) VALUES (?, ?)`,
          "assistant",
          assistantMess
        );
        db.run("COMMIT");

        return new Response(
          JSON.stringify({ success: true, message: "2 rows inserted." }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      } catch (err) {
        console.log(err);
        try {
          db.run("ROLLBACK");
        } catch (rbErr) {
          console.log('rollback error', rbErr)
        }
        return new Response(
          JSON.stringify({ error: `DB transaction failed: ${err}` }),
          { status: 500, headers: { "Content-Type": "application/json" } }
        );
      }
      }
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
