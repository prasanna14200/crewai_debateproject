import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from debate.crew import Debate


logger = logging.getLogger(__name__)
app = FastAPI(title="CrewAI Debate")
executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="debate")
jobs: dict[str, dict[str, str]] = {}
jobs_lock = threading.Lock()
active_job: str | None = None


class DebateRequest(BaseModel):
    motion: str = Field(min_length=5, max_length=500)


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f7f8f4">
  <title>CrewAI Debate</title>
  <style>
    :root { color-scheme: light; --ink: #172d2b; --muted: #62716c; --line: #d9e1dc; --paper: #f7f8f4; --white: #fff; --green: #176b57; --coral: #bf573f; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--paper); color: var(--ink); font: 16px/1.55 system-ui, sans-serif; }
    header { border-bottom: 1px solid var(--line); background: var(--white); }
    .topline, main { width: min(100% - 40px, 960px); margin-inline: auto; }
    .topline { min-height: 64px; display: flex; align-items: center; justify-content: space-between; gap: 20px; }
    .brand { color: var(--ink); font-size: 14px; font-weight: 750; letter-spacing: .08em; text-decoration: none; text-transform: uppercase; }
    .model { color: var(--muted); font-size: 12px; }
    main { padding-block: 56px 80px; }
    h1 { max-width: 640px; margin: 0; font: 500 clamp(36px, 6vw, 62px)/1.02 Georgia, serif; letter-spacing: 0; }
    .intro { color: var(--muted); margin: 14px 0 32px; }
    form { padding: 20px; background: var(--white); border: 1px solid var(--line); border-top: 3px solid var(--green); }
    label { display: block; margin-bottom: 10px; font-size: 13px; font-weight: 700; }
    textarea { display: block; width: 100%; min-height: 112px; padding: 14px; border: 1px solid var(--line); border-radius: 3px; resize: vertical; color: var(--ink); font: inherit; }
    textarea:focus { outline: 2px solid var(--green); outline-offset: 2px; }
    .form-footer { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-top: 14px; }
    button { min-height: 44px; padding: 0 20px; border: 0; border-radius: 3px; background: var(--green); color: white; font: inherit; font-weight: 700; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    #status { min-height: 24px; color: var(--muted); font-size: 13px; }
    #status.error { color: #a3362d; }
    #results { margin-top: 40px; }
    .section-title { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; border-bottom: 1px solid var(--line); padding-bottom: 10px; margin-bottom: 16px; }
    h2 { margin: 0; font: 500 28px/1.2 Georgia, serif; letter-spacing: 0; }
    .motion-label { color: var(--muted); font-size: 13px; }
    .arguments { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    article { min-width: 0; padding: 20px; border: 1px solid var(--line); background: var(--white); }
    article h3 { margin: 0 0 12px; font-size: 13px; text-transform: uppercase; }
    article p { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; }
    .propose { border-top: 3px solid var(--green); }
    .oppose { border-top: 3px solid var(--coral); }
    .decision { margin-top: 16px; border-left: 4px solid var(--green); background: #e8f0eb; }
    [hidden] { display: none !important; }
    @media (max-width: 620px) {
      .topline, main { width: min(100% - 28px, 960px); }
      main { padding-top: 36px; }
      .arguments { grid-template-columns: 1fr; }
      .form-footer { align-items: flex-start; flex-direction: column; }
      .model { max-width: 48%; text-align: right; }
    }
  </style>
</head>
<body>
  <header><div class="topline"><a class="brand" href="/">Debate / CrewAI</a><span class="model">Hugging Face · Llama 3 8B Instruct</span></div></header>
  <main>
    <h1>Put a motion to the test.</h1>
    <p class="intro">Two arguments. One judgment.</p>
    <form id="debate-form">
      <label for="motion">Motion</label>
      <textarea id="motion" name="motion" minlength="5" maxlength="500" placeholder="Should cities ban private cars from downtown areas?" required></textarea>
      <div class="form-footer"><span id="status" role="status" aria-live="polite"></span><button id="submit" type="submit">Start debate</button></div>
    </form>
    <section id="results" aria-live="polite" hidden>
      <div class="section-title"><h2>Arguments</h2><span id="result-motion" class="motion-label"></span></div>
      <div class="arguments">
        <article class="propose"><h3>Proposition</h3><p id="propose"></p></article>
        <article class="oppose"><h3>Opposition</h3><p id="oppose"></p></article>
      </div>
      <article class="decision"><h3>Judge's decision</h3><p id="decision"></p></article>
    </section>
  </main>
  <script>
    const form = document.querySelector('#debate-form');
    const button = document.querySelector('#submit');
    const status = document.querySelector('#status');
    const results = document.querySelector('#results');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      button.disabled = true;
      status.classList.remove('error');
      status.textContent = 'The agents are preparing their arguments…';
      results.hidden = true;
      try {
        const response = await fetch('/debate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ motion: document.querySelector('#motion').value })
        });
        const started = await response.json();
        if (!response.ok) throw new Error(started.detail || 'The debate could not be started.');
        let data;
        while (true) {
          await new Promise((resolve) => setTimeout(resolve, 2000));
          const poll = await fetch(`/debate/${started.job_id}`);
          data = await poll.json();
          if (!poll.ok) throw new Error(data.detail || 'The debate status could not be read.');
          if (data.status === 'completed') break;
          if (data.status === 'failed') throw new Error(data.detail);
          status.textContent = data.status === 'queued' ? 'Waiting for the debate to start…' : 'The agents are preparing their arguments…';
        }
        document.querySelector('#result-motion').textContent = data.motion;
        document.querySelector('#propose').textContent = data.propose;
        document.querySelector('#oppose').textContent = data.oppose;
        document.querySelector('#decision').textContent = data.decision;
        results.hidden = false;
        status.textContent = 'Debate complete';
      } catch (error) {
        status.textContent = error.message;
        status.classList.add('error');
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return PAGE


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _execute_debate(job_id: str, motion: str) -> None:
    global active_job
    with jobs_lock:
        jobs[job_id]["status"] = "running"

    try:
        result = Debate().crew().kickoff(inputs={"motion": motion})
        outputs = result.tasks_output
        if len(outputs) < 3:
            raise RuntimeError("The debate did not produce all three task outputs.")
        update = {
            "status": "completed",
            "motion": motion,
            "propose": outputs[0].raw,
            "oppose": outputs[1].raw,
            "decision": outputs[2].raw,
        }
    except Exception:
        logger.exception("Debate execution failed")
        update = {
            "status": "failed",
            "motion": motion,
            "detail": "Debate failed. Check the configured model and server logs.",
        }

    with jobs_lock:
        jobs[job_id].update(update)
        active_job = None


@app.post("/debate", status_code=202)
def run_debate(request: DebateRequest) -> dict[str, str]:
    global active_job
    motion = request.motion.strip()
    if len(motion) < 5:
        raise HTTPException(status_code=422, detail="Enter a motion of at least 5 characters.")

    with jobs_lock:
        if active_job is not None:
            raise HTTPException(status_code=409, detail="A debate is already running. Try again shortly.")
        finished_jobs = [job_id for job_id, job in jobs.items() if job["status"] in {"completed", "failed"}]
        while len(jobs) >= 25 and finished_jobs:
            del jobs[finished_jobs.pop(0)]
        if len(jobs) >= 25:
            raise HTTPException(status_code=503, detail="The debate queue is full. Try again later.")

        job_id = str(uuid4())
        jobs[job_id] = {"status": "queued", "motion": motion}
        active_job = job_id

    try:
        executor.submit(_execute_debate, job_id, motion)
    except Exception as error:
        with jobs_lock:
            jobs.pop(job_id, None)
            active_job = None
        raise HTTPException(status_code=503, detail="The debate could not be queued.") from error
    return {"job_id": job_id, "status": "queued"}


@app.get("/debate/{job_id}")
def get_debate(job_id: str) -> dict[str, str]:
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Debate not found.")
        return job.copy()