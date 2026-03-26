import { json } from '@sveltejs/kit';
import { getDb } from '$lib/server/db';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
  const db = await getDb();
  const flowType = url.searchParams.get('flow_type');
  const filter: Record<string, unknown> = {};
  if (flowType) filter.flow_type = flowType;

  const flows = await db
    .collection('flows')
    .find(filter, { projection: { nodes: 0, edges: 0 } })
    .sort({ updated_at: -1 })
    .toArray();

  const result = flows.map((f) => ({
    ...f,
    _id: f._id.toString(),
    node_count: f.node_count ?? 0
  }));

  return json(result);
};

export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json();
  const db = await getDb();

  const slug =
    body.slug ||
    body.name
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');

  const doc = {
    tenant_id: body.tenant_id || 'tenant_1',
    name: body.name,
    slug,
    status: body.status || 'draft',
    flow_type: body.flow_type || 'quote',
    version: 1,
    nodes: body.nodes || [],
    edges: body.edges || [],
    pricing_csv: body.pricing_csv || '',
    node_count: (body.nodes || []).length,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  const result = await db.collection('flows').insertOne(doc);

  return json({ ...doc, _id: result.insertedId.toString() }, { status: 201 });
};
