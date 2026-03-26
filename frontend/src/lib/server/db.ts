import { MongoClient, type Db } from 'mongodb';
import { env } from '$env/dynamic/private';

let client: MongoClient;
let db: Db;

export async function getDb(): Promise<Db> {
  if (db) return db;

  const uri = env.MONGODB_URI;
  if (!uri) throw new Error('MONGODB_URI not set');

  client = new MongoClient(uri);
  await client.connect();
  db = client.db(env.MONGODB_DATABASE || 'flowquote');

  return db;
}
