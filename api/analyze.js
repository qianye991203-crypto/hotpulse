export const runtime = 'edge';

export async function POST(request) {
  const { prompt, apiKey } = await request.json();
  
  if (!apiKey) {
    return Response.json({ error: 'Missing API key' }, { status: 400 });
  }

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{ role: 'user', content: prompt }]
    })
  });

  const data = await res.json();
  return Response.json(data);
}