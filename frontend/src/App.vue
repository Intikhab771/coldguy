<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// --- CORE APP STATE ---
const emailList = ref([{ target_email: '', subject: '', body: '' }])
const isAutoMode = ref(false)
const frequencySeconds = ref(150)
const aiGlitchActive = ref(false)

// --- CAMPAIGN TRACKER STATE ---
const totalTarget = ref(1) // Default strictly set to 1
const emailsSent = ref(0)
let statusInterval: ReturnType<typeof setInterval> | null = null

// --- ATTACHMENT STATE ---
const selectedFiles = ref<File[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

// --- AI GENERATOR VARIABLES ---
const jobTitle = ref('Senior UI Dev')
const companyName = ref('Fintech Stealth Startup')
const jobDescription = ref('')
const resumeText = ref("B.Tech student at NIT Silchar. Strong in C++, Data Structures & Algorithms. Built a full-stack asynchronous cold email automation platform using FastAPI, Vue.js, and Google's SMTP servers.")
const userName = ref("Cold Guy")
const userLinks = ref("github.com/coldguy")

// --- BUTTON ANIMATION STATE ---
const isSending = ref(false)
const sendBtnText = ref('SEND CAMPAIGN')
const loaderFrames = ['[=     ]', '[==    ]', '[===   ]', '[ ===  ]', '[  === ]', '[   ===]', '[    ==]', '[     =]', '[    ==]', '[   ===]', '[  === ]', '[ ===  ]', '[===   ]', '[==    ]']

// --- COUNTER LOGIC (Least Count = 1 Constraint) ---
const decreaseTarget = () => {
  totalTarget.value = Math.max(1, totalTarget.value - 1)
}

const increaseTarget = () => {
  totalTarget.value += 1
}

// --- SYNC LIVE FREQUENCY TO BACKEND ---
const pushFrequencyToBackend = async () => {
  const fd = new FormData()
  fd.append('frequency', frequencySeconds.value.toString())
  try {
    await fetch('http://127.0.0.1:8000/api/update-frequency', { method: 'POST', body: fd })
  } catch (error) {
    console.error("Failed to push live frequency change.", error)
  }
}

// --- SYNC STATUS FROM BACKEND ---
const fetchStatus = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/campaign-status')
    if (res.ok) {
      const data = await res.json()
      emailsSent.value = data.emails_sent
    }
  } catch (error) {
    console.error("Tracker sync failed. Backend might be down.")
  }
}

onMounted(() => {
  // Sped up polling to 1s so the UI catches the tolerance delay precisely
  statusInterval = setInterval(fetchStatus, 1000)
})

onUnmounted(() => {
  if (statusInterval) clearInterval(statusInterval)
})

// --- THE AI GENERATOR FUNCTION ---
const generateAIEmail = async () => {
  emailList.value[0].subject = "ANALYZING TARGET..."
  emailList.value[0].body = "Generating highly personalized copy..."
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/generate-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_title: jobTitle.value,
        company_name: companyName.value,
        job_description: jobDescription.value,
        resume_text: resumeText.value,
        user_name: userName.value,
        user_links: userLinks.value
      })
    })
    
    const data = await response.json()
    if (data.status === "Success") {
      emailList.value[0].subject = data.subject
      emailList.value[0].body = data.body
    } else {
      emailList.value[0].subject = "AI ERROR"
      emailList.value[0].body = "Failed to generate. Check backend logs."
    }
  } catch (error) {
    emailList.value[0].subject = "CONNECTION FAILED"
    emailList.value[0].body = "Is the FastAPI server running?"
  }
}

// --- FILE HANDLING LOGIC ---
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFiles.value.push(...Array.from(target.files))
  }
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
  if (fileInput.value) {
    fileInput.value.value = '' 
  }
}

// --- THE SEND CAMPAIGN FUNCTION ---
const startCampaign = async () => {
  if (isSending.value) return
  isSending.value = true
  
  let frameIdx = 0
  const animInterval = setInterval(() => {
    sendBtnText.value = `${loaderFrames[frameIdx]} TX...`
    frameIdx = (frameIdx + 1) % loaderFrames.length
  }, 100)

  const formData = new FormData()
  formData.append('campaign_data', JSON.stringify(emailList.value))
  formData.append('is_auto_mode', isAutoMode.value.toString())
  formData.append('frequency', frequencySeconds.value.toString())
  formData.append('total_target', totalTarget.value.toString())
  
  selectedFiles.value.forEach(file => {
    formData.append('attachments', file)
  })

  try {
    const response = await fetch('http://127.0.0.1:8000/api/send-bulk', { method: 'POST', body: formData })
    
    clearInterval(animInterval)
    sendBtnText.value = "[OK] SENT"
    
    // Resync immediately
    await fetchStatus()
    
    setTimeout(() => {
      sendBtnText.value = "SEND CAMPAIGN"
      isSending.value = false
    }, 2000)

  } catch (error) {
    clearInterval(animInterval)
    sendBtnText.value = "[ERR] SERVER DOWN"
    setTimeout(() => {
      sendBtnText.value = "SEND CAMPAIGN"
      isSending.value = false
    }, 2000)
  }
}

// --- UI HELPERS ---
const triggerAiGlitch = () => {
  aiGlitchActive.value = false
  setTimeout(() => aiGlitchActive.value = true, 10)
  setTimeout(() => aiGlitchActive.value = false, 200)
}

const handleAiToggle = async () => {
  triggerAiGlitch()
  if (isAutoMode.value) {
    await generateAIEmail()
  }
}
</script>

<template>
  <div class="bg-surface text-on-surface font-body-md h-screen flex flex-row overflow-x-auto overflow-y-hidden">
    
    <nav class="flex flex-col h-screen w-64 left-0 sticky bg-surface-container border-r-3 border-on-surface shadow-[6px_0px_0px_0px_#1a1c1c] py-gutter gap-stack-gap z-50 brutal-border-r shrink-0">
      <div class="px-gutter pb-4 brutal-border-b mb-4 flex flex-col gap-2">
        <h1 class="font-headline-md text-headline-md font-black text-on-surface italic tracking-tighter">#COLDGUY</h1>
        <div class="flex items-center gap-3 mt-2">
          <div class="w-10 h-10 bg-primary brutal-border brutal-shadow-sm flex items-center justify-center overflow-hidden">
            <div class="w-full h-full bg-black"></div>
          </div>
          <div>
            <div class="font-label-bold text-label-bold text-on-surface uppercase">OPERATOR_01</div>
            <div class="font-code-sm text-code-sm text-tertiary uppercase">Rank: Gold</div>
          </div>
        </div>
        <button class="mt-4 w-full bg-primary text-on-primary font-label-bold text-label-bold uppercase brutal-border brutal-shadow brutal-button py-3 px-4 flex justify-center items-center gap-2">
          <span class="material-symbols-outlined" data-icon="add" data-weight="fill" style="font-variation-settings: 'FILL' 1;">add</span>
          NEW CAMPAIGN
        </button>
      </div>
      <div class="flex-1 overflow-y-auto px-2 flex flex-col gap-2">
        <a class="font-body-md text-body-md uppercase text-on-surface-variant hover:text-on-surface px-4 py-3 hover:bg-surface-container-high transition-all flex items-center gap-3 relative overflow-hidden" href="#">
          <span class="material-symbols-outlined" data-icon="dashboard">dashboard</span> Dashboard
        </a>
        <a class="font-body-md text-body-md uppercase bg-secondary text-on-secondary border-3 border-on-surface shadow-[4px_4px_0px_0px_#1a1c1c] mx-2 my-1 px-4 py-3 flex items-center gap-3 brutal-border brutal-shadow relative overflow-hidden" href="#">
          <span class="material-symbols-outlined" data-icon="local_fire_department" data-weight="fill" style="font-variation-settings: 'FILL' 1;">local_fire_department</span> Hot Jobs
        </a>
        <a class="font-body-md text-body-md uppercase text-on-surface-variant hover:text-on-surface px-4 py-3 hover:bg-surface-container-high transition-all flex items-center gap-3 relative overflow-hidden" href="#">
          <span class="material-symbols-outlined" data-icon="description">description</span> Templates
        </a>
        <a class="font-body-md text-body-md uppercase text-on-surface-variant hover:text-on-surface px-4 py-3 hover:bg-surface-container-high transition-all flex items-center gap-3 relative overflow-hidden" href="#">
          <span class="material-symbols-outlined" data-icon="bolt">bolt</span> Automation
        </a>
        <a class="font-body-md text-body-md uppercase text-on-surface-variant hover:text-on-surface px-4 py-3 hover:bg-surface-container-high transition-all flex items-center gap-3 relative overflow-hidden" href="#">
          <span class="material-symbols-outlined" data-icon="history">history</span> History
        </a>
      </div>
      <div class="px-gutter pt-4 brutal-border-t mt-auto flex flex-col gap-2">
        <a class="font-body-md text-body-md uppercase text-on-surface-variant hover:text-on-surface py-2 flex items-center gap-3 relative overflow-hidden" href="#">
          <span class="material-symbols-outlined" data-icon="help">help</span> Support
        </a>
        <a class="font-body-md text-body-md uppercase text-on-surface-variant hover:text-on-surface py-2 flex items-center gap-3 relative overflow-hidden" href="#">
          <span class="material-symbols-outlined" data-icon="logout">logout</span> Log Out
        </a>
      </div>
    </nav>

    <main class="flex-1 flex flex-row relative min-w-max">
      <div class="absolute inset-0 pointer-events-none opacity-5" style="background-image: radial-gradient(#1a1c1c 2px, transparent 2px); background-size: 24px 24px;"></div>
      
      <section class="w-[400px] brutal-border-r bg-surface-container-lowest overflow-y-auto z-10 flex flex-col shrink-0 h-screen">
        <div class="sticky top-0 bg-surface-container-lowest p-gutter brutal-border-b z-20 flex justify-between items-center">
          <h2 class="font-headline-lg font-extrabold uppercase text-on-surface flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-4xl" data-icon="local_fire_department" data-weight="fill" style="font-variation-settings: 'FILL' 1;">local_fire_department</span>
            HOT JOBS
          </h2>
          <div class="bg-secondary text-on-secondary font-label-bold text-label-bold brutal-border px-3 py-1 brutal-shadow">LIVE</div>
        </div>
        <div class="p-gutter flex flex-col gap-6">
          <article class="bg-surface brutal-border brutal-shadow p-6 relative group transition-transform hover:-translate-y-1">
            <div class="absolute top-0 right-0 bg-primary text-on-primary font-code-sm text-code-sm px-3 py-1 brutal-border-l brutal-border-b font-bold tracking-widest uppercase">URGENT</div>
            <div class="mb-4">
              <span class="inline-block bg-secondary-container text-on-secondary-container font-label-bold text-label-bold px-2 py-1 brutal-border mb-2">ENG-04</span>
              <h3 class="font-headline-md text-headline-md font-bold uppercase leading-tight mb-1">Senior UI Dev</h3>
              <p class="font-body-md text-body-md text-tertiary">Fintech Stealth Startup</p>
            </div>
            <div class="brutal-border-t pt-4 flex justify-between items-end">
              <div>
                <div class="font-code-sm text-code-sm text-on-surface font-bold uppercase mb-1">Match Score</div>
                <div class="font-headline-md text-headline-md text-primary font-black">94%</div>
              </div>
              <button class="bg-surface text-on-surface brutal-border p-2 brutal-shadow brutal-button hover:bg-secondary transition-colors" title="Load Lead">
                <span class="material-symbols-outlined" data-icon="arrow_forward">arrow_forward</span>
              </button>
            </div>
          </article>
          <article class="bg-surface brutal-border brutal-shadow p-6 relative group transition-transform hover:-translate-y-1">
            <div class="mb-4">
              <span class="inline-block bg-surface-dim text-on-surface font-label-bold text-label-bold px-2 py-1 brutal-border mb-2">MKT-12</span>
              <h3 class="font-headline-md text-headline-md font-bold uppercase leading-tight mb-1">Growth Hacker</h3>
              <p class="font-body-md text-body-md text-tertiary">SaaS Scale-up (B2B)</p>
            </div>
            <div class="brutal-border-t pt-4 flex justify-between items-end">
              <div>
                <div class="font-code-sm text-code-sm text-on-surface font-bold uppercase mb-1">Match Score</div>
                <div class="font-headline-md text-headline-md text-on-surface font-black">88%</div>
              </div>
              <button class="bg-surface text-on-surface brutal-border p-2 brutal-shadow brutal-button hover:bg-secondary transition-colors" title="Load Lead">
                <span class="material-symbols-outlined" data-icon="arrow_forward">arrow_forward</span>
              </button>
            </div>
          </article>
          <article class="bg-surface brutal-border brutal-shadow p-6 relative group transition-transform hover:-translate-y-1 opacity-70">
            <div class="mb-4">
              <span class="inline-block bg-surface-dim text-on-surface font-label-bold text-label-bold px-2 py-1 brutal-border mb-2">SLS-88</span>
              <h3 class="font-headline-md text-headline-md font-bold uppercase leading-tight mb-1">Outbound AE</h3>
              <p class="font-body-md text-body-md text-tertiary">Cybersecurity</p>
            </div>
            <div class="brutal-border-t pt-4 flex justify-between items-end">
              <div>
                <div class="font-code-sm text-code-sm text-on-surface font-bold uppercase mb-1">Match Score</div>
                <div class="font-headline-md text-headline-md text-tertiary font-black">72%</div>
              </div>
              <button class="bg-surface text-on-surface brutal-border p-2 brutal-shadow brutal-button hover:bg-secondary transition-colors" title="Load Lead">
                <span class="material-symbols-outlined" data-icon="arrow_forward">arrow_forward</span>
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="flex-1 min-w-[600px] flex flex-col z-10 bg-background overflow-y-auto h-screen">
        <div class="p-gutter brutal-border-b bg-secondary-container flex flex-wrap justify-between items-center gap-4 shrink-0">
          <div>
            <h2 class="font-headline-md text-headline-md font-extrabold uppercase text-on-secondary-container mb-1">Campaign Architect</h2>
            <p class="font-code-sm text-code-sm text-on-secondary-container font-bold">MODE: AGGRESSIVE_OUTBOUND</p>
          </div>
          <div class="flex items-center gap-3 bg-surface p-3 brutal-border brutal-shadow shrink-0">
            <button @click="generateAIEmail" :class="{'label-glitch-active': aiGlitchActive}" class="font-label-bold text-label-bold uppercase text-on-surface flex items-center gap-1 hover:text-primary transition-colors cursor-pointer border-none bg-transparent">
              <span class="material-symbols-outlined text-primary" data-icon="auto_awesome" data-weight="fill" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
              AI ENHANCE
            </button>
            <label class="hard-toggle-wrapper ml-2">
              <input type="checkbox" v-model="isAutoMode" @change="handleAiToggle" class="hard-toggle-input"/>
              <div class="hard-toggle-well">
                <div class="hard-toggle-handle"></div>
              </div>
            </label>
          </div>
        </div>

        <div class="mt-6 mx-6 p-6 bg-surface brutal-border brutal-shadow flex flex-col gap-4 shrink-0">
          <h3 class="font-headline-md text-headline-md font-extrabold uppercase text-on-surface">CAMPAIGN PROGRESS</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <div class="flex flex-col gap-2">
              <label class="font-label-bold text-label-bold uppercase bg-on-surface text-surface px-2 py-1 inline-block w-max brutal-border">TOTAL TARGET</label>
              <div class="flex items-center gap-4 bg-surface-container-low brutal-border p-4 brutal-shadow-sm">
                <button @click="decreaseTarget" class="w-12 h-12 bg-primary text-on-primary brutal-border brutal-shadow brutal-button flex items-center justify-center font-black text-2xl"> - </button>
                <span class="flex-1 text-center font-headline-md text-headline-md font-black">{{ totalTarget }}</span>
                <button @click="increaseTarget" class="w-12 h-12 bg-primary text-on-primary brutal-border brutal-shadow brutal-button flex items-center justify-center font-black text-2xl"> + </button>
              </div>
            </div>
            
            <div class="flex flex-col gap-2">
              <label class="font-label-bold text-label-bold uppercase bg-on-surface text-surface px-2 py-1 inline-block w-max brutal-border">EMAILS SENT</label>
              <div class="flex items-center justify-center bg-secondary-container brutal-border p-4 brutal-shadow-sm h-full">
                <div class="font-headline-md text-headline-md font-black text-on-secondary-container">
                  {{ emailsSent }} / <span>{{ totalTarget }}</span>
                </div>
              </div>
            </div>
            
          </div>
        </div>

        <div class="flex-1 p-gutter flex flex-col gap-6">
          <div class="grid grid-cols-2 gap-6">
            <div class="flex flex-col gap-2">
              <label class="font-label-bold text-label-bold uppercase bg-on-surface text-surface px-2 py-1 inline-block w-max brutal-border">TARGET EMAIL</label>
              <div class="relative">
                <input v-model="emailList[0].target_email" class="w-full bg-surface brutal-border p-4 font-body-md text-body-md text-on-surface brutal-shadow brutal-input" placeholder="Enter target email..." type="email"/>
                <span class="absolute right-4 top-4 material-symbols-outlined text-tertiary" data-icon="verified" data-weight="fill" style="font-variation-settings: 'FILL' 1; color: #5e6300;">verified</span>
              </div>
            </div>
            <div class="flex flex-col gap-2">
              <label class="font-label-bold text-label-bold uppercase bg-on-surface text-surface px-2 py-1 inline-block w-max brutal-border">VARIABLE: {COMPANY}</label>
              <input v-model="companyName" class="w-full bg-surface brutal-border p-4 font-body-md text-body-md text-on-surface brutal-shadow brutal-input" placeholder="Company Name..." type="text"/>
            </div>
          </div>
          
          <div class="flex flex-col gap-2 mt-2">
            <label class="font-label-bold text-label-bold uppercase bg-on-surface text-surface px-2 py-1 inline-block w-max brutal-border">SUBJECT</label>
            <input v-model="emailList[0].subject" class="w-full bg-surface brutal-border p-4 font-body-lg text-body-lg text-on-surface font-bold brutal-shadow brutal-input" placeholder="Subject line..." type="text"/>
          </div>
          
          <div class="flex flex-col gap-2 min-h-[300px] mt-2">
            <div class="flex justify-between items-end">
              <label class="font-label-bold text-label-bold uppercase bg-on-surface text-surface px-2 py-1 inline-block w-max brutal-border">MESSAGE BODY</label>
              <div class="font-code-sm text-code-sm text-tertiary">Spam Score: <span class="text-secondary font-bold">LOW</span></div>
            </div>
            <textarea v-model="emailList[0].body" class="w-full min-h-[300px] bg-surface brutal-border p-6 font-body-md text-body-md text-on-surface brutal-shadow brutal-input resize-y leading-relaxed" placeholder="Type your message here..."></textarea>
          </div>
          
          <div class="flex flex-col gap-4 mt-4">
            <label class="font-label-bold text-label-bold uppercase bg-on-surface text-surface px-2 py-1 inline-block w-max brutal-border">ATTACHMENTS</label>
            <div class="w-full border-3 border-dashed border-on-surface bg-surface-container-low p-8 flex flex-col items-center justify-center gap-4 brutal-shadow-sm">
              <span class="material-symbols-outlined text-4xl text-tertiary" data-icon="upload_file">upload_file</span>
              <div class="text-center">
                <p class="font-label-bold text-label-bold uppercase text-on-surface">DRAG &amp; DROP RESUMES OR DOCUMENTS</p>
                <p class="font-code-sm text-code-sm text-tertiary mt-1">MAX FILE SIZE: 10MB EACH</p>
              </div>
              
              <input type="file" ref="fileInput" class="hidden" multiple @change="handleFileChange" />
              
              <button @click="triggerFileInput" class="bg-primary text-on-primary font-label-bold text-label-bold uppercase brutal-border brutal-shadow brutal-button py-2 px-6">
                BROWSE FILES
              </button>
            </div>
            
            <div v-if="selectedFiles.length > 0" class="flex flex-col gap-2">
              <h4 class="font-code-sm text-code-sm text-on-surface font-bold uppercase">ATTACHED FILES</h4>
              <div v-for="(file, index) in selectedFiles" :key="index" class="flex items-center justify-between bg-surface brutal-border p-3 brutal-shadow-sm">
                <div class="flex items-center gap-3 overflow-hidden">
                  <span class="material-symbols-outlined text-primary shrink-0" data-icon="description">description</span>
                  <span class="font-body-md text-body-md truncate">{{ file.name }}</span>
                </div>
                <button @click="removeFile(index)" class="bg-[#ff3e3e] text-white font-code-sm text-code-sm font-bold uppercase brutal-border px-3 py-1 brutal-button shrink-0 ml-2">
                  REMOVE
                </button>
              </div>
            </div>
          </div>
          
          <div class="mt-4 p-6 bg-surface-container-high brutal-border brutal-shadow flex flex-row gap-8 items-center justify-between">
            <div class="w-1/2 flex flex-col gap-3">
              <div class="flex justify-between items-center">
                <label class="font-label-bold text-label-bold uppercase text-on-surface">SEND RATE / FREQUENCY</label>
                <span class="font-code-sm text-code-sm bg-surface brutal-border px-2 py-1 font-bold">{{ frequencySeconds }}s</span>
              </div>
              
              <input v-model="frequencySeconds" @change="pushFrequencyToBackend" class="w-full h-3 bg-surface-dim brutal-border appearance-none cursor-pointer accent-primary" max="500" min="10" type="range"/>
              
              <div class="flex justify-between font-code-sm text-code-sm text-tertiary">
                <span>Safe</span>
                <span>Aggressive</span>
              </div>
            </div>
            
            <button @click="startCampaign" class="relative overflow-hidden bg-primary text-on-primary font-headline-md text-headline-md font-black uppercase brutal-border brutal-shadow-lg py-4 px-12 send-button-interactive animate-brutal-pulse flex items-center justify-center gap-3 hover:bg-surface-tint transition-all shrink-0" :disabled="isSending">
              <div class="shimmer-effect"></div>
              <span class="material-symbols-outlined text-3xl relative z-10" data-icon="send" data-weight="fill" style="font-variation-settings: 'FILL' 1;">send</span>
              <span class="relative z-10 font-code-sm font-bold text-xl">{{ sendBtnText }}</span>
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
.material-symbols-outlined.filled { font-variation-settings: 'FILL' 1; }

/* Brutalist Base Styles */
body { background-color: #f9f9f9; color: #1a1c1c; overflow-x: hidden; cursor: crosshair !important; }
a, button, input, textarea, label { cursor: crosshair !important; }

/* Custom Scrollbar */
::-webkit-scrollbar { width: 12px; background: #f9f9f9; border-left: 3px solid #1a1c1c; }
::-webkit-scrollbar-thumb { background: #1a1c1c; border: 3px solid #1a1c1c; }

/* Specific Brutalist utilities */
.brutal-shadow { box-shadow: 4px 4px 0px 0px #1a1c1c; }
.brutal-shadow-sm { box-shadow: 2px 2px 0px 0px #1a1c1c; }
.brutal-shadow-lg { box-shadow: 8px 8px 0px 0px #1a1c1c; }
.brutal-border { border: 3px solid #1a1c1c; }
.brutal-border-b { border-bottom: 3px solid #1a1c1c; }
.brutal-border-r { border-right: 3px solid #1a1c1c; }
.brutal-border-t { border-top: 3px solid #1a1c1c; }
.brutal-border-l { border-left: 3px solid #1a1c1c; }

.brutal-button { transition: all 0.1s ease-in-out; }
.brutal-button:active { transform: translate(4px, 4px); box-shadow: 0px 0px 0px 0px #1a1c1c; }
.brutal-input:focus { background-color: #e1ec3a; outline: none; }

/* Hard-Shift Toggle Switch */
.hard-toggle-wrapper { position: relative; display: inline-block; width: 48px; height: 24px; cursor: crosshair !important; }
.hard-toggle-input { display: none; }
.hard-toggle-well { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: #e2e2e2; border: 3px solid #1a1c1c; transition: background-color 0s; cursor: crosshair !important; }
.hard-toggle-handle { position: absolute; top: -6px; left: -6px; width: 30px; height: 30px; background-color: #ffffff; border: 3px solid #1a1c1c; box-shadow: 4px 4px 0px 0px #1a1c1c; transition: transform 0.15s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.1s ease; }
.hard-toggle-input:checked + .hard-toggle-well { background-color: #ff3e3e; }
.hard-toggle-input:checked + .hard-toggle-well .hard-toggle-handle { transform: translateX(24px); }
.hard-toggle-well:active .hard-toggle-handle { transform: scale(0.9) translate(4px, 4px); box-shadow: 0px 0px 0px 0px #1a1c1c; }
.hard-toggle-input:checked + .hard-toggle-well:active .hard-toggle-handle { transform: translateX(24px) scale(0.9) translate(4px, 4px); box-shadow: 0px 0px 0px 0px #1a1c1c; }

/* Glitch Flicker Animation */
@keyframes label-glitch { 0% { transform: translate(0) } 20% { transform: translate(-2px, 1px) } 40% { transform: translate(2px, -1px) } 60% { transform: translate(-1px, 2px) } 80% { transform: translate(1px, -2px) } 100% { transform: translate(0) } }
.label-glitch-active { animation: label-glitch 0.2s steps(2, end); color: #1a1c1c; text-shadow: 2px 0 #1a1c1c, -2px 0 #1a1c1c; }

/* Animated Button Specific Styles */
@keyframes brutal-pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.01); } }
.animate-brutal-pulse { animation: brutal-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes shimmer { 0% { transform: translateX(-150%) skewX(-20deg); } 100% { transform: translateX(250%) skewX(-20deg); } }
.shimmer-effect { position: absolute; top: 0; left: 0; width: 40%; height: 100%; background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.4), transparent); animation: shimmer 3s infinite; }
.send-button-interactive { transition: transform 0.1s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.1s ease; }
.send-button-interactive:hover { transform: scale(1.02); box-shadow: 12px 12px 0px 0px #1a1c1c; }
.send-button-interactive:active { transform: translate(8px, 8px) scale(1.0); box-shadow: 0px 0px 0px 0px #1a1c1c; }

/* VHS / CRT Hover Effects */
@keyframes glitch-skew { 0% { transform: skew(0deg); } 20% { transform: skew(-2deg); } 40% { transform: skew(2deg); } 60% { transform: skew(-1deg); } 80% { transform: skew(1deg); } 100% { transform: skew(0deg); } }
@keyframes rgb-split { 0% { text-shadow: -2px 0 #bb0018, 2px 0 #e1ec3a; } 50% { text-shadow: 2px 0 #bb0018, -2px 0 #e1ec3a; } 100% { text-shadow: -2px 0 #bb0018, 2px 0 #e1ec3a; } }
.brutal-button:hover, nav a:hover, .send-button-interactive:hover { animation: glitch-skew 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94) both infinite, rgb-split 0.15s linear infinite; position: relative; }
.brutal-button:hover::after, nav a:hover::after, .send-button-interactive:hover::after { content: " "; display: block; position: absolute; top: 0; left: 0; bottom: 0; right: 0; background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%); z-index: 2; background-size: 100% 4px; pointer-events: none; }
</style>