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

  const flow = await db.collection('flows').findOne(filter);
  if (!flow) throw error(404, 'Flow nao encontrado');

  return json({ ...flow, _id: flow._id.toString() });
};

export const PUT: RequestHandler = async ({ params, request }) => {
  const body = await request.json();
  const db = await getDb();

  let oid: ObjectId;
  try {
    oid = new ObjectId(params.id);
  } catch {
    throw error(400, 'ID invalido');
  }

  const existing = await db.collection('flows').findOne({ _id: oid });
  if (!existing) throw error(404, 'Flow nao encontrado');

  const update = {
    name: body.name ?? existing.name,
    slug:
      body.slug ||
      (body.name || existing.name)
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, ''),
    status: body.status ?? existing.status,
    version: (existing.version || 0) + 1,
    nodes: body.nodes ?? existing.nodes,
    edges: body.edges ?? existing.edges,
    pricing_csv: body.pricing_csv ?? existing.pricing_csv ?? '',
    node_count: (body.nodes ?? existing.nodes).length,
    updated_at: new Date().toISOString()
  };

  await db.collection('flows').updateOne({ _id: oid }, { $set: update });

  return json({ ...existing, ...update, _id: params.id });
};

export const DELETE: RequestHandler = async ({ params }) => {
  const db = await getDb();

  let oid: ObjectId;
  try {
    oid = new ObjectId(params.id);
  } catch {
    throw error(400, 'ID invalido');
  }

  const result = await db.collection('flows').deleteOne({ _id: oid });
  if (result.deletedCount === 0) throw error(404, 'Flow nao encontrado');

  return json({ ok: true });
};
