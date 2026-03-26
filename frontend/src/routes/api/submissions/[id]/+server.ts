import { json, error } from '@sveltejs/kit';
import { ObjectId } from 'mongodb';
import { getDb } from '$lib/server/db';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params }) => {
  const db = await getDb();

  let filter: Record<string, unknown>;
  try {
    filter = { _id: new ObjectId(params.id) };
  } catch {
    throw error(400, 'ID invalido');
  }

  const sub = await db.collection('submissions').findOne(filter);
  if (!sub) throw error(404, 'Submission nao encontrada');

  return json({ ...sub, id: sub._id.toString(), _id: undefined });
};
