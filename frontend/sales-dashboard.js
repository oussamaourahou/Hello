// ============================================================
// Sales Dashboard — Prototype with Mock Data
// ============================================================

// ---- Mock Data ----

const MOCK_DATA = {
    '7days': {
        outbound: {
            campaigns: [
                { name: 'Spring Promo 2026', sent: 4200, delivered: 3948, read: 3024, replies: 462 },
                { name: 'New Listings Feb', sent: 3100, delivered: 2914, read: 2206, replies: 341 },
                { name: 'Re-engagement Q1', sent: 2800, delivered: 2548, read: 1732, replies: 196 },
                { name: 'VIP Early Access', sent: 1500, delivered: 1455, read: 1310, replies: 289 },
                { name: 'Weekend Flash Sale', sent: 2200, delivered: 2090, read: 1672, replies: 312 },
                { name: 'Insurance Renewal', sent: 1800, delivered: 1674, read: 1172, replies: 134 },
                { name: 'Auto Showcase Invite', sent: 950, delivered: 912, read: 730, replies: 168 },
                { name: 'Follow-up Warm Leads', sent: 680, delivered: 666, read: 586, replies: 203 },
            ],
        },
        inbound: {
            total: 1247,
            outOfTarget: 448,
            interested: 519,
            highlyInterested: 243,
            unclassified: 37,
        },
        messages: {
            total: 8432,
            text: 5186,
            image: 2103,
            voice: 1143,
        },
        sla: {
            aiMedianSeconds: 45,
            aiWithin2minPct: 94.2,
            humanMedianMinutes: 28,
            humanWithin1hPct: 78.5,
        },
        unanswered: [
            { contact: 'Ahmed Benali', phone: '+212 6XX-XXX-401', lastMessageTime: '2026-02-16T08:12:00', type: 'text', owner: 'Sarah M.', ageMinutes: 185 },
            { contact: 'Fatima Zahra', phone: '+212 6XX-XXX-402', lastMessageTime: '2026-02-16T07:45:00', type: 'voice', owner: 'Unassigned', ageMinutes: 212 },
            { contact: 'Youssef Amrani', phone: '+212 6XX-XXX-403', lastMessageTime: '2026-02-16T07:30:00', type: 'text', owner: 'Karim L.', ageMinutes: 227 },
            { contact: 'Nadia Bouzid', phone: '+212 6XX-XXX-404', lastMessageTime: '2026-02-16T06:55:00', type: 'image', owner: 'Sarah M.', ageMinutes: 262 },
            { contact: 'Omar Tazi', phone: '+212 6XX-XXX-405', lastMessageTime: '2026-02-16T06:20:00', type: 'text', owner: 'Unassigned', ageMinutes: 297 },
            { contact: 'Khadija El Idrissi', phone: '+212 6XX-XXX-406', lastMessageTime: '2026-02-16T05:48:00', type: 'text', owner: 'Amine R.', ageMinutes: 329 },
            { contact: 'Rachid Fassi', phone: '+212 6XX-XXX-407', lastMessageTime: '2026-02-16T05:10:00', type: 'voice', owner: 'Unassigned', ageMinutes: 367 },
            { contact: 'Salma Chaoui', phone: '+212 6XX-XXX-408', lastMessageTime: '2026-02-16T04:33:00', type: 'text', owner: 'Karim L.', ageMinutes: 404 },
            { contact: 'Hassan Berrada', phone: '+212 6XX-XXX-409', lastMessageTime: '2026-02-16T03:50:00', type: 'image', owner: 'Unassigned', ageMinutes: 447 },
            { contact: 'Layla Mansouri', phone: '+212 6XX-XXX-410', lastMessageTime: '2026-02-16T03:15:00', type: 'text', owner: 'Sarah M.', ageMinutes: 482 },
            { contact: 'Mehdi Alaoui', phone: '+212 6XX-XXX-411', lastMessageTime: '2026-02-16T02:40:00', type: 'text', owner: 'Amine R.', ageMinutes: 517 },
            { contact: 'Zineb Ouazzani', phone: '+212 6XX-XXX-412', lastMessageTime: '2026-02-16T02:05:00', type: 'voice', owner: 'Unassigned', ageMinutes: 552 },
            { contact: 'Anas Kettani', phone: '+212 6XX-XXX-413', lastMessageTime: '2026-02-16T01:20:00', type: 'text', owner: 'Karim L.', ageMinutes: 597 },
            { contact: 'Imane Benjelloun', phone: '+212 6XX-XXX-414', lastMessageTime: '2026-02-15T23:45:00', type: 'text', owner: 'Unassigned', ageMinutes: 692 },
            { contact: 'Driss Cherkaoui', phone: '+212 6XX-XXX-415', lastMessageTime: '2026-02-15T22:30:00', type: 'image', owner: 'Sarah M.', ageMinutes: 767 },
            { contact: 'Houda Filali', phone: '+212 6XX-XXX-416', lastMessageTime: '2026-02-15T21:10:00', type: 'text', owner: 'Amine R.', ageMinutes: 847 },
            { contact: 'Tariq Bennani', phone: '+212 6XX-XXX-417', lastMessageTime: '2026-02-15T20:00:00', type: 'text', owner: 'Unassigned', ageMinutes: 917 },
            { contact: 'Samira Hajji', phone: '+212 6XX-XXX-418', lastMessageTime: '2026-02-15T18:45:00', type: 'voice', owner: 'Karim L.', ageMinutes: 992 },
            { contact: 'Kamal Ziani', phone: '+212 6XX-XXX-419', lastMessageTime: '2026-02-15T17:20:00', type: 'text', owner: 'Unassigned', ageMinutes: 1077 },
            { contact: 'Rania Squalli', phone: '+212 6XX-XXX-420', lastMessageTime: '2026-02-15T16:05:00', type: 'text', owner: 'Sarah M.', ageMinutes: 1152 },
            { contact: 'Badr Tahiri', phone: '+212 6XX-XXX-421', lastMessageTime: '2026-02-15T14:40:00', type: 'image', owner: 'Amine R.', ageMinutes: 1237 },
            { contact: 'Ghita Sefrioui', phone: '+212 6XX-XXX-422', lastMessageTime: '2026-02-15T13:15:00', type: 'text', owner: 'Unassigned', ageMinutes: 1322 },
            { contact: 'Adil Lahlou', phone: '+212 6XX-XXX-423', lastMessageTime: '2026-02-15T11:50:00', type: 'voice', owner: 'Karim L.', ageMinutes: 1407 },
        ],
        // Mock drill-down replies per campaign
        campaignReplies: {
            'Spring Promo 2026': [
                { contact: 'Ahmed B.', phone: '+212 6XX-001', replyTime: '2m 14s', message: 'Yes interested, send me details!' },
                { contact: 'Fatima Z.', phone: '+212 6XX-002', replyTime: '5m 40s', message: 'What are the prices?' },
                { contact: 'Youssef A.', phone: '+212 6XX-003', replyTime: '12m 03s', message: 'Can I visit tomorrow?' },
                { contact: 'Nadia B.', phone: '+212 6XX-004', replyTime: '1h 22m', message: 'Not right now, maybe later' },
            ],
            'VIP Early Access': [
                { contact: 'Omar T.', phone: '+212 6XX-005', replyTime: '45s', message: 'Count me in!' },
                { contact: 'Khadija E.', phone: '+212 6XX-006', replyTime: '3m 10s', message: 'What time does it start?' },
                { contact: 'Rachid F.', phone: '+212 6XX-007', replyTime: '8m 55s', message: 'Perfect, I will bring my wife' },
            ],
        },
        // Mock funnel conversations
        funnelConversations: {
            total: [
                { contact: 'Ahmed Benali', tags: 'property_inquiry, high_budget', lastMessage: '10 min ago', assignee: 'Sarah M.' },
                { contact: 'Fatima Zahra', tags: 'test_drive_request', lastMessage: '25 min ago', assignee: 'Karim L.' },
                { contact: 'Youssef Amrani', tags: 'spam, wrong_number', lastMessage: '1h ago', assignee: 'Unassigned' },
            ],
            outOfTarget: [
                { contact: 'Youssef Amrani', tags: 'spam, wrong_number', lastMessage: '1h ago', assignee: 'Unassigned' },
                { contact: 'Nadia Bouzid', tags: 'competitor_inquiry', lastMessage: '2h ago', assignee: 'Unassigned' },
                { contact: 'Rachid Fassi', tags: 'out_of_area', lastMessage: '3h ago', assignee: 'Unassigned' },
            ],
            interested: [
                { contact: 'Omar Tazi', tags: 'general_inquiry, mid_budget', lastMessage: '15 min ago', assignee: 'Sarah M.' },
                { contact: 'Salma Chaoui', tags: 'appointment_request', lastMessage: '45 min ago', assignee: 'Karim L.' },
                { contact: 'Khadija El Idrissi', tags: 'quote_request', lastMessage: '1h 20min ago', assignee: 'Amine R.' },
            ],
            highlyInterested: [
                { contact: 'Ahmed Benali', tags: 'property_inquiry, high_budget, urgent', lastMessage: '10 min ago', assignee: 'Sarah M.' },
                { contact: 'Fatima Zahra', tags: 'test_drive_request, repeat_customer', lastMessage: '25 min ago', assignee: 'Karim L.' },
                { contact: 'Layla Mansouri', tags: 'ready_to_buy, premium_tier', lastMessage: '30 min ago', assignee: 'Amine R.' },
            ],
        },
    },

    'today': {
        outbound: {
            campaigns: [
                { name: 'Spring Promo 2026', sent: 620, delivered: 583, read: 447, replies: 68 },
                { name: 'New Listings Feb', sent: 450, delivered: 423, read: 320, replies: 49 },
                { name: 'VIP Early Access', sent: 210, delivered: 204, read: 184, replies: 41 },
            ],
        },
        inbound: {
            total: 184,
            outOfTarget: 66,
            interested: 76,
            highlyInterested: 35,
            unclassified: 7,
        },
        messages: {
            total: 1241,
            text: 764,
            image: 309,
            voice: 168,
        },
        sla: {
            aiMedianSeconds: 38,
            aiWithin2minPct: 96.1,
            humanMedianMinutes: 22,
            humanWithin1hPct: 82.3,
        },
        unanswered: [
            { contact: 'Ahmed Benali', phone: '+212 6XX-XXX-401', lastMessageTime: '2026-02-16T08:12:00', type: 'text', owner: 'Sarah M.', ageMinutes: 185 },
            { contact: 'Fatima Zahra', phone: '+212 6XX-XXX-402', lastMessageTime: '2026-02-16T07:45:00', type: 'voice', owner: 'Unassigned', ageMinutes: 212 },
            { contact: 'Youssef Amrani', phone: '+212 6XX-XXX-403', lastMessageTime: '2026-02-16T07:30:00', type: 'text', owner: 'Karim L.', ageMinutes: 227 },
            { contact: 'Nadia Bouzid', phone: '+212 6XX-XXX-404', lastMessageTime: '2026-02-16T06:55:00', type: 'image', owner: 'Sarah M.', ageMinutes: 262 },
            { contact: 'Omar Tazi', phone: '+212 6XX-XXX-405', lastMessageTime: '2026-02-16T06:20:00', type: 'text', owner: 'Unassigned', ageMinutes: 297 },
        ],
        campaignReplies: {
            'Spring Promo 2026': [
                { contact: 'Ahmed B.', phone: '+212 6XX-001', replyTime: '1m 52s', message: 'Interested! Send more info' },
                { contact: 'Fatima Z.', phone: '+212 6XX-002', replyTime: '4m 20s', message: 'What is the location?' },
            ],
        },
        funnelConversations: {
            total: [
                { contact: 'Ahmed Benali', tags: 'property_inquiry, high_budget', lastMessage: '10 min ago', assignee: 'Sarah M.' },
            ],
            outOfTarget: [
                { contact: 'Youssef Amrani', tags: 'spam', lastMessage: '1h ago', assignee: 'Unassigned' },
            ],
            interested: [
                { contact: 'Omar Tazi', tags: 'general_inquiry', lastMessage: '15 min ago', assignee: 'Sarah M.' },
            ],
            highlyInterested: [
                { contact: 'Ahmed Benali', tags: 'property_inquiry, high_budget, urgent', lastMessage: '10 min ago', assignee: 'Sarah M.' },
            ],
        },
    },

    '30days': {
        outbound: {
            campaigns: [
                { name: 'Spring Promo 2026', sent: 12600, delivered: 11844, read: 9072, replies: 1386 },
                { name: 'New Listings Feb', sent: 9300, delivered: 8742, read: 6618, replies: 1023 },
                { name: 'Re-engagement Q1', sent: 8400, delivered: 7644, read: 5196, replies: 588 },
                { name: 'VIP Early Access', sent: 4500, delivered: 4365, read: 3930, replies: 867 },
                { name: 'Weekend Flash Sale', sent: 6600, delivered: 6270, read: 5016, replies: 936 },
                { name: 'Insurance Renewal', sent: 5400, delivered: 5022, read: 3516, replies: 402 },
                { name: 'Auto Showcase Invite', sent: 2850, delivered: 2736, read: 2190, replies: 504 },
                { name: 'Follow-up Warm Leads', sent: 2040, delivered: 1998, read: 1758, replies: 609 },
                { name: 'January Clearance', sent: 7200, delivered: 6768, read: 4740, replies: 576 },
                { name: 'Referral Bonus', sent: 3400, delivered: 3298, read: 2638, replies: 495 },
            ],
        },
        inbound: {
            total: 5340,
            outOfTarget: 1922,
            interested: 2224,
            highlyInterested: 1041,
            unclassified: 153,
        },
        messages: {
            total: 36120,
            text: 22214,
            image: 9011,
            voice: 4895,
        },
        sla: {
            aiMedianSeconds: 52,
            aiWithin2minPct: 91.8,
            humanMedianMinutes: 34,
            humanWithin1hPct: 74.1,
        },
        unanswered: [
            { contact: 'Ahmed Benali', phone: '+212 6XX-XXX-401', lastMessageTime: '2026-02-16T08:12:00', type: 'text', owner: 'Sarah M.', ageMinutes: 185 },
            { contact: 'Fatima Zahra', phone: '+212 6XX-XXX-402', lastMessageTime: '2026-02-16T07:45:00', type: 'voice', owner: 'Unassigned', ageMinutes: 212 },
            { contact: 'Youssef Amrani', phone: '+212 6XX-XXX-403', lastMessageTime: '2026-02-16T07:30:00', type: 'text', owner: 'Karim L.', ageMinutes: 227 },
            { contact: 'Nadia Bouzid', phone: '+212 6XX-XXX-404', lastMessageTime: '2026-02-16T06:55:00', type: 'image', owner: 'Sarah M.', ageMinutes: 262 },
            { contact: 'Omar Tazi', phone: '+212 6XX-XXX-405', lastMessageTime: '2026-02-16T06:20:00', type: 'text', owner: 'Unassigned', ageMinutes: 297 },
            { contact: 'Khadija El Idrissi', phone: '+212 6XX-XXX-406', lastMessageTime: '2026-02-16T05:48:00', type: 'text', owner: 'Amine R.', ageMinutes: 329 },
            { contact: 'Rachid Fassi', phone: '+212 6XX-XXX-407', lastMessageTime: '2026-02-16T05:10:00', type: 'voice', owner: 'Unassigned', ageMinutes: 367 },
            { contact: 'Salma Chaoui', phone: '+212 6XX-XXX-408', lastMessageTime: '2026-02-16T04:33:00', type: 'text', owner: 'Karim L.', ageMinutes: 404 },
            { contact: 'Hassan Berrada', phone: '+212 6XX-XXX-409', lastMessageTime: '2026-02-16T03:50:00', type: 'image', owner: 'Unassigned', ageMinutes: 447 },
            { contact: 'Layla Mansouri', phone: '+212 6XX-XXX-410', lastMessageTime: '2026-02-16T03:15:00', type: 'text', owner: 'Sarah M.', ageMinutes: 482 },
            { contact: 'Mehdi Alaoui', phone: '+212 6XX-XXX-411', lastMessageTime: '2026-02-16T02:40:00', type: 'text', owner: 'Amine R.', ageMinutes: 517 },
            { contact: 'Zineb Ouazzani', phone: '+212 6XX-XXX-412', lastMessageTime: '2026-02-16T02:05:00', type: 'voice', owner: 'Unassigned', ageMinutes: 552 },
            { contact: 'Anas Kettani', phone: '+212 6XX-XXX-413', lastMessageTime: '2026-02-16T01:20:00', type: 'text', owner: 'Karim L.', ageMinutes: 597 },
            { contact: 'Imane Benjelloun', phone: '+212 6XX-XXX-414', lastMessageTime: '2026-02-15T23:45:00', type: 'text', owner: 'Unassigned', ageMinutes: 692 },
            { contact: 'Driss Cherkaoui', phone: '+212 6XX-XXX-415', lastMessageTime: '2026-02-15T22:30:00', type: 'image', owner: 'Sarah M.', ageMinutes: 767 },
            { contact: 'Houda Filali', phone: '+212 6XX-XXX-416', lastMessageTime: '2026-02-15T21:10:00', type: 'text', owner: 'Amine R.', ageMinutes: 847 },
            { contact: 'Tariq Bennani', phone: '+212 6XX-XXX-417', lastMessageTime: '2026-02-15T20:00:00', type: 'text', owner: 'Unassigned', ageMinutes: 917 },
            { contact: 'Samira Hajji', phone: '+212 6XX-XXX-418', lastMessageTime: '2026-02-15T18:45:00', type: 'voice', owner: 'Karim L.', ageMinutes: 992 },
            { contact: 'Kamal Ziani', phone: '+212 6XX-XXX-419', lastMessageTime: '2026-02-15T17:20:00', type: 'text', owner: 'Unassigned', ageMinutes: 1077 },
            { contact: 'Rania Squalli', phone: '+212 6XX-XXX-420', lastMessageTime: '2026-02-15T16:05:00', type: 'text', owner: 'Sarah M.', ageMinutes: 1152 },
            { contact: 'Badr Tahiri', phone: '+212 6XX-XXX-421', lastMessageTime: '2026-02-15T14:40:00', type: 'image', owner: 'Amine R.', ageMinutes: 1237 },
            { contact: 'Ghita Sefrioui', phone: '+212 6XX-XXX-422', lastMessageTime: '2026-02-15T13:15:00', type: 'text', owner: 'Unassigned', ageMinutes: 1322 },
            { contact: 'Adil Lahlou', phone: '+212 6XX-XXX-423', lastMessageTime: '2026-02-15T11:50:00', type: 'voice', owner: 'Karim L.', ageMinutes: 1407 },
            { contact: 'Soukaina Mrini', phone: '+212 6XX-XXX-424', lastMessageTime: '2026-02-15T10:20:00', type: 'text', owner: 'Unassigned', ageMinutes: 1497 },
            { contact: 'Hamza Belhaj', phone: '+212 6XX-XXX-425', lastMessageTime: '2026-02-15T08:55:00', type: 'text', owner: 'Sarah M.', ageMinutes: 1582 },
            { contact: 'Wiam Larbi', phone: '+212 6XX-XXX-426', lastMessageTime: '2026-02-15T07:30:00', type: 'image', owner: 'Amine R.', ageMinutes: 1667 },
            { contact: 'Nabil Tahri', phone: '+212 6XX-XXX-427', lastMessageTime: '2026-02-15T06:10:00', type: 'voice', owner: 'Unassigned', ageMinutes: 1747 },
            { contact: 'Amina Slaoui', phone: '+212 6XX-XXX-428', lastMessageTime: '2026-02-15T04:45:00', type: 'text', owner: 'Karim L.', ageMinutes: 1832 },
        ],
        campaignReplies: {
            'Spring Promo 2026': [
                { contact: 'Ahmed B.', phone: '+212 6XX-001', replyTime: '2m 14s', message: 'Yes interested, send me details!' },
                { contact: 'Fatima Z.', phone: '+212 6XX-002', replyTime: '5m 40s', message: 'What are the prices?' },
                { contact: 'Youssef A.', phone: '+212 6XX-003', replyTime: '12m 03s', message: 'Can I visit tomorrow?' },
                { contact: 'Nadia B.', phone: '+212 6XX-004', replyTime: '1h 22m', message: 'Not right now, maybe later' },
                { contact: 'Omar T.', phone: '+212 6XX-005', replyTime: '30s', message: 'Perfect timing!' },
            ],
        },
        funnelConversations: {
            total: [
                { contact: 'Ahmed Benali', tags: 'property_inquiry, high_budget', lastMessage: '10 min ago', assignee: 'Sarah M.' },
                { contact: 'Fatima Zahra', tags: 'test_drive_request', lastMessage: '25 min ago', assignee: 'Karim L.' },
                { contact: 'Youssef Amrani', tags: 'spam, wrong_number', lastMessage: '1h ago', assignee: 'Unassigned' },
                { contact: 'Nadia Bouzid', tags: 'competitor_inquiry', lastMessage: '2h ago', assignee: 'Unassigned' },
            ],
            outOfTarget: [
                { contact: 'Youssef Amrani', tags: 'spam, wrong_number', lastMessage: '1h ago', assignee: 'Unassigned' },
                { contact: 'Nadia Bouzid', tags: 'competitor_inquiry', lastMessage: '2h ago', assignee: 'Unassigned' },
                { contact: 'Rachid Fassi', tags: 'out_of_area', lastMessage: '3h ago', assignee: 'Unassigned' },
                { contact: 'Hassan Berrada', tags: 'wrong_product', lastMessage: '5h ago', assignee: 'Unassigned' },
            ],
            interested: [
                { contact: 'Omar Tazi', tags: 'general_inquiry, mid_budget', lastMessage: '15 min ago', assignee: 'Sarah M.' },
                { contact: 'Salma Chaoui', tags: 'appointment_request', lastMessage: '45 min ago', assignee: 'Karim L.' },
                { contact: 'Khadija El Idrissi', tags: 'quote_request', lastMessage: '1h 20min ago', assignee: 'Amine R.' },
                { contact: 'Mehdi Alaoui', tags: 'comparison_shopping', lastMessage: '2h ago', assignee: 'Unassigned' },
            ],
            highlyInterested: [
                { contact: 'Ahmed Benali', tags: 'property_inquiry, high_budget, urgent', lastMessage: '10 min ago', assignee: 'Sarah M.' },
                { contact: 'Fatima Zahra', tags: 'test_drive_request, repeat_customer', lastMessage: '25 min ago', assignee: 'Karim L.' },
                { contact: 'Layla Mansouri', tags: 'ready_to_buy, premium_tier', lastMessage: '30 min ago', assignee: 'Amine R.' },
                { contact: 'Zineb Ouazzani', tags: 'urgent, VIP', lastMessage: '1h ago', assignee: 'Sarah M.' },
            ],
        },
    },
};

// ---- State ----

let currentDateRange = '7days';
let campaignSortField = 'replies';
let campaignSortAsc = false;
let unansweredSortField = 'age';
let unansweredSortAsc = false;

// ---- Top-level Tab Switching ----

function switchTopTab(tab) {
    document.querySelectorAll('.top-nav-tab').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.top-tab-content').forEach(el => el.classList.remove('active'));

    if (tab === 'pipeline') {
        document.querySelector('.top-nav-tab:nth-child(1)').classList.add('active');
        document.getElementById('pipelineView').classList.add('active');
    } else {
        document.querySelector('.top-nav-tab:nth-child(2)').classList.add('active');
        document.getElementById('salesDashboardView').classList.add('active');
        renderDashboard();
    }
}

// ---- Dashboard Sub-tab Switching ----

function switchDashboardTab(tab) {
    document.querySelectorAll('.dashboard-tab').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.dashboard-tab-content').forEach(el => el.classList.remove('active'));

    const tabMap = {
        'cockpit': { btnIdx: 0, contentId: 'cockpitTab' },
        'outbound': { btnIdx: 1, contentId: 'outboundTab' },
        'inbound': { btnIdx: 2, contentId: 'inboundTab' },
        'sla': { btnIdx: 3, contentId: 'slaTab' },
    };

    const info = tabMap[tab];
    document.querySelectorAll('.dashboard-tab')[info.btnIdx].classList.add('active');
    document.getElementById(info.contentId).classList.add('active');
}

// ---- Filters ----

function applyDashboardFilters() {
    currentDateRange = document.getElementById('dateRangeFilter').value;
    renderDashboard();
}

// ---- Helpers ----

function formatNumber(n) {
    return n.toLocaleString('en-US');
}

function pct(part, whole) {
    if (whole === 0) return '0.0';
    return ((part / whole) * 100).toFixed(1);
}

function formatAge(minutes) {
    if (minutes < 60) return minutes + 'm';
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    if (h < 24) return h + 'h ' + m + 'm';
    const d = Math.floor(h / 24);
    const remainH = h % 24;
    return d + 'd ' + remainH + 'h';
}

function formatTime(isoString) {
    const d = new Date(isoString);
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) +
        ' ' + d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function messageTypeIcon(type) {
    switch (type) {
        case 'text': return 'TXT';
        case 'image': return 'IMG';
        case 'voice': return 'VCE';
        default: return type.toUpperCase();
    }
}

// ---- Main Render ----

function renderDashboard() {
    const data = MOCK_DATA[currentDateRange];
    if (!data) return;

    renderCockpit(data);
    renderOutbound(data);
    renderInbound(data);
    renderSla(data);
    renderUnanswered(data);
}

// ---- Cockpit ----

function renderCockpit(data) {
    const campaigns = data.outbound.campaigns;
    const totalSent = campaigns.reduce((s, c) => s + c.sent, 0);
    const totalDelivered = campaigns.reduce((s, c) => s + c.delivered, 0);
    const totalRead = campaigns.reduce((s, c) => s + c.read, 0);
    const totalReplies = campaigns.reduce((s, c) => s + c.replies, 0);

    document.getElementById('kpiTotalCampaigns').textContent = campaigns.length;
    document.getElementById('kpiDeliveryRate').textContent = pct(totalDelivered, totalSent) + '%';
    document.getElementById('kpiReadRate').textContent = pct(totalRead, totalSent) + '%';
    document.getElementById('kpiReplyRate').textContent = pct(totalReplies, totalSent) + '%';

    document.getElementById('kpiTotalInbound').textContent = formatNumber(data.inbound.total);
    document.getElementById('kpiOutOfTarget').textContent = formatNumber(data.inbound.outOfTarget);
    document.getElementById('kpiInterested').textContent = formatNumber(data.inbound.interested);
    document.getElementById('kpiHighlyInterested').textContent = formatNumber(data.inbound.highlyInterested);

    document.getElementById('kpiTotalMessages').textContent = formatNumber(data.messages.total);
    document.getElementById('kpiMessageBreakdown').innerHTML =
        '<span class="msg-type">Text: ' + formatNumber(data.messages.text) + ' (' + pct(data.messages.text, data.messages.total) + '%)</span>' +
        '<span class="msg-type">Image: ' + formatNumber(data.messages.image) + ' (' + pct(data.messages.image, data.messages.total) + '%)</span>' +
        '<span class="msg-type">Voice: ' + formatNumber(data.messages.voice) + ' (' + pct(data.messages.voice, data.messages.total) + '%)</span>';

    document.getElementById('kpiAiSlaMedian').textContent = data.sla.aiMedianSeconds + 's';
    document.getElementById('kpiAiSlaPercent').textContent = data.sla.aiWithin2minPct + '% within 2 min';

    document.getElementById('kpiHumanSlaMedian').textContent = data.sla.humanMedianMinutes + 'min';
    document.getElementById('kpiHumanSlaPercent').textContent = data.sla.humanWithin1hPct + '% within 1h';

    document.getElementById('kpiUnanswered').textContent = data.unanswered.length;
}

// ---- Outbound ----

function renderOutbound(data) {
    const campaigns = data.outbound.campaigns;
    const totalSent = campaigns.reduce((s, c) => s + c.sent, 0);
    const totalDelivered = campaigns.reduce((s, c) => s + c.delivered, 0);
    const totalRead = campaigns.reduce((s, c) => s + c.read, 0);
    const totalReplies = campaigns.reduce((s, c) => s + c.replies, 0);

    document.getElementById('outboundTotalCampaigns').textContent = campaigns.length;
    document.getElementById('outboundTotalSent').textContent = formatNumber(totalSent);
    document.getElementById('outboundGlobalDelivery').textContent = pct(totalDelivered, totalSent) + '%';
    document.getElementById('outboundGlobalRead').textContent = pct(totalRead, totalSent) + '%';
    document.getElementById('outboundGlobalReply').textContent = pct(totalReplies, totalSent) + '%';

    renderCampaignTable(data);
}

function renderCampaignTable(data) {
    const campaigns = data.outbound.campaigns.map(c => ({
        ...c,
        deliveredPct: c.sent > 0 ? (c.delivered / c.sent) * 100 : 0,
        readPct: c.sent > 0 ? (c.read / c.sent) * 100 : 0,
        replyPct: c.sent > 0 ? (c.replies / c.sent) * 100 : 0,
    }));

    campaigns.sort((a, b) => {
        let valA = a[campaignSortField];
        let valB = b[campaignSortField];
        if (typeof valA === 'string') {
            valA = valA.toLowerCase();
            valB = valB.toLowerCase();
        }
        if (campaignSortAsc) return valA > valB ? 1 : -1;
        return valA < valB ? 1 : -1;
    });

    const tbody = document.getElementById('campaignTableBody');
    tbody.innerHTML = campaigns.map(c => `
        <tr class="campaign-row" onclick="openCampaignDrilldown('${c.name.replace(/'/g, "\\'")}')">
            <td>${c.name}</td>
            <td class="num">${formatNumber(c.sent)}</td>
            <td class="num">${formatNumber(c.delivered)}</td>
            <td class="num">${c.deliveredPct.toFixed(1)}%</td>
            <td class="num">${formatNumber(c.read)}</td>
            <td class="num">${c.readPct.toFixed(1)}%</td>
            <td class="num">${formatNumber(c.replies)}</td>
            <td class="num">${c.replyPct.toFixed(1)}%</td>
        </tr>
    `).join('');
}

function sortCampaignTable(field) {
    if (campaignSortField === field) {
        campaignSortAsc = !campaignSortAsc;
    } else {
        campaignSortField = field;
        campaignSortAsc = false;
    }
    renderCampaignTable(MOCK_DATA[currentDateRange]);
}

function openCampaignDrilldown(campaignName) {
    const data = MOCK_DATA[currentDateRange];
    const replies = data.campaignReplies[campaignName] || [
        { contact: 'Sample Contact', phone: '+212 6XX-XXX', replyTime: '3m 15s', message: 'I am interested in this offer' },
        { contact: 'Another Lead', phone: '+212 6XX-YYY', replyTime: '11m 42s', message: 'Can you share more details?' },
    ];

    document.getElementById('drilldownCampaignName').textContent = campaignName;
    document.getElementById('drilldownTableBody').innerHTML = replies.map(r => `
        <tr>
            <td>${r.contact}</td>
            <td>${r.phone}</td>
            <td>${r.replyTime}</td>
            <td>${r.message}</td>
        </tr>
    `).join('');

    document.getElementById('campaignDrilldown').style.display = 'block';
}

function closeCampaignDrilldown() {
    document.getElementById('campaignDrilldown').style.display = 'none';
}

// ---- Inbound Funnel ----

function renderInbound(data) {
    const inb = data.inbound;
    const maxVal = inb.total;

    const steps = [
        { label: 'Total Inbound', value: inb.total, color: '#667eea', key: 'total' },
        { label: 'Out of Target', value: inb.outOfTarget, color: '#e74c3c', key: 'outOfTarget' },
        { label: 'Interested', value: inb.interested, color: '#f39c12', key: 'interested' },
        { label: 'Highly Interested', value: inb.highlyInterested, color: '#2ecc71', key: 'highlyInterested' },
    ];

    if (inb.unclassified > 0) {
        steps.push({ label: 'Unclassified', value: inb.unclassified, color: '#95a5a6', key: 'unclassified' });
    }

    const container = document.getElementById('funnelContainer');
    container.innerHTML = steps.map((step, i) => {
        const widthPct = maxVal > 0 ? Math.max((step.value / maxVal) * 100, 15) : 15;
        const conversionFromTotal = maxVal > 0 ? ((step.value / maxVal) * 100).toFixed(1) : '0.0';
        return `
            <div class="funnel-step" onclick="openFunnelDrilldown('${step.key}', '${step.label}')" title="Click to see conversations">
                <div class="funnel-bar-row">
                    <span class="funnel-label">${step.label}</span>
                    <div class="funnel-bar" style="width:${widthPct}%;background:${step.color};">
                        <span class="funnel-bar-value">${formatNumber(step.value)}</span>
                    </div>
                    <span class="funnel-pct">${conversionFromTotal}%</span>
                </div>
            </div>
        `;
    }).join('');
}

function openFunnelDrilldown(key, label) {
    const data = MOCK_DATA[currentDateRange];
    const conversations = data.funnelConversations[key] || data.funnelConversations.total;

    document.getElementById('funnelDrilldownTitle').textContent = label + ' Conversations';
    document.getElementById('funnelDrilldownBody').innerHTML = conversations.map(c => `
        <tr>
            <td>${c.contact}</td>
            <td><span class="tag-list">${c.tags}</span></td>
            <td>${c.lastMessage}</td>
            <td>${c.assignee}</td>
        </tr>
    `).join('');

    document.getElementById('funnelDrilldown').style.display = 'block';
}

function closeFunnelDrilldown() {
    document.getElementById('funnelDrilldown').style.display = 'none';
}

// ---- SLA ----

function renderSla(data) {
    const sla = data.sla;

    document.getElementById('slaAiMedian').textContent = sla.aiMedianSeconds + 's';
    document.getElementById('slaAiWithin2m').textContent = sla.aiWithin2minPct + '%';
    document.getElementById('slaAiBar').style.width = sla.aiWithin2minPct + '%';

    document.getElementById('slaHumanMedian').textContent = sla.humanMedianMinutes + ' min';
    document.getElementById('slaHumanWithin1h').textContent = sla.humanWithin1hPct + '%';
    document.getElementById('slaHumanBar').style.width = sla.humanWithin1hPct + '%';
}

// ---- Unanswered ----

function renderUnanswered(data) {
    const unanswered = [...data.unanswered];

    unanswered.sort((a, b) => {
        let valA, valB;
        if (unansweredSortField === 'age') {
            valA = a.ageMinutes;
            valB = b.ageMinutes;
        } else {
            valA = new Date(a.lastMessageTime).getTime();
            valB = new Date(b.lastMessageTime).getTime();
        }
        if (unansweredSortAsc) return valA > valB ? 1 : -1;
        return valA < valB ? 1 : -1;
    });

    document.getElementById('unansweredBadge').textContent = unanswered.length;

    document.getElementById('unansweredTableBody').innerHTML = unanswered.map(u => `
        <tr>
            <td>
                <div class="contact-cell">
                    <strong>${u.contact}</strong>
                    <small>${u.phone}</small>
                </div>
            </td>
            <td>${formatTime(u.lastMessageTime)}</td>
            <td><span class="msg-type-badge msg-type-${u.type}">${messageTypeIcon(u.type)}</span></td>
            <td><span class="${u.owner === 'Unassigned' ? 'owner-unassigned' : ''}">${u.owner}</span></td>
            <td><span class="age-badge ${u.ageMinutes > 480 ? 'age-critical' : u.ageMinutes > 240 ? 'age-warning' : 'age-normal'}">${formatAge(u.ageMinutes)}</span></td>
        </tr>
    `).join('');
}

function sortUnansweredTable(field) {
    if (unansweredSortField === field) {
        unansweredSortAsc = !unansweredSortAsc;
    } else {
        unansweredSortField = field;
        unansweredSortAsc = false;
    }
    renderUnanswered(MOCK_DATA[currentDateRange]);
}

// ---- Initialize on load (if dashboard is visible) ----
// Dashboard renders when the Sales Dashboard tab is clicked.
