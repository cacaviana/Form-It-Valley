import { json } from '@sveltejs/kit';
import { getDb } from '$lib/server/db';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
  const db = await getDb();
  const submissions = await db
    .collection('submissions')
    .find()
    .sort({ created_at: -1 })
    .limit(200)
    .toArray();

  const result = submissions.map((s) => ({
    ...s,
    id: s._id.toString(),
    _id: undefined,
    has_quote: !!s.quote_text
  }));

  return json({ submissions: result, total: result.length });
};

export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json();
  const db = await getDb();

  const doc = {
    tenant_id: body.tenant_id || 'tenant_1',
    flow_id: body.flow_id,
    flow_slug: body.flow_slug,
    client_name: body.client_name,
    client_email: body.client_email,
    client_phone: body.client_phone || null,
    client_address: body.client_address || null,
    answers: body.answers || [],
    end_node_id: body.end_node_id,
    end_type: body.end_type || 'quote',
    quote_text: null,
    status: 'pending',
    created_at: new Date().toISOString()
  };

  const result = await db.collection('submissions').insertOne(doc);

  return json(
    {
      id: result.insertedId.toString(),
      ...doc,
      status: 'quoted'
    },
    { status: 201 }
  );
};
