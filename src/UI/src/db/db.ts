import {Database} from 'bun:sqlite';

// Open (or create) the database
const db = new Database("localDB");
try {
 db
  .query("SELECT * FROM convs LIMIT 1")
  .all();
} catch {
db.run(`
        CREATE TABLE IF NOT EXISTS convs (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            blobImg BLOB NOT NULL
        )
    `);

    const rows = [
    { name: "Alice", blobImg: new Uint8Array([1,2,3]) },
    { name: "Bob", blobImg: new Uint8Array([4,5,6]) },
    { name: "Charlie", blobImg: new Uint8Array([7,8,9]) },
    { name: "Diana", blobImg: new Uint8Array([10,11,12]) },
    ];

    for (const row of rows) {
        db.run(
            "INSERT INTO convs (name, blobImg) VALUES (?, ?)",
            [row.name,
            row.blobImg]
        );
    }
    const convs = db.query("SELECT id, name FROM convs").all() as {id: number, name: string}[];

    for (const conv of convs) {
        const tableName = `${conv.id}-${conv.name}`;

        // Quote the table name to allow characters like '-' or spaces
        const quoted = `"${tableName.replace(/"/g, '""')}"`;

        // Create the table if not exists
        db.run(`
            CREATE TABLE IF NOT EXISTS ${quoted} (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                sender TEXT NOT NULL,
                content TEXT NOT NULL
            )
        `);
    }

}

export default db;