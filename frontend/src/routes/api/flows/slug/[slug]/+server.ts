import { json, error } from '@sveltejs/kit';
import { getDb } from '$lib/server/db';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params }) => {
  const db = await getDb();
  const flow = await db.collection('flows').findOne({ slug: params.slug });
  if (!flow) throw error(404, 'Flow nao encontrado');

  return json({ ...flow, _id: flow._id.toString() });
};
