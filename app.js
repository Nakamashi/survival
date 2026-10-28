'use strict';

const ITEMS = [
  { id: 'fishing', name: 'Fishing rod', file: 'rod.jpeg' },
  { id: 'matches', name: 'Matches (10)', file: 'matches.jpeg' },
  { id: 'rope', name: 'Rope (20 metres)', file: 'rope.jpeg' },
  { id: 'pot', name: 'Cooking pot', file: 'pot.jpeg' },
  { id: 'aid', name: 'First aid kit', file: 'first aid.jpeg' },
  { id: 'food', name: 'Food for 7 days', file: 'food.jpeg' },
  { id: 'flashlight', name: 'Flashlight', file: 'flashlight.jpeg' },
  { id: 'flare', name: 'Emergency flare gun (3 shots)', file: 'flare.jpeg' },
  { id: 'blanket', name: 'Blanket', file: 'blanket.jpeg' },
  { id: 'phone', name: 'Smartphone (no signal)', file: 'phone.jpeg' },
];
const STORAGE_KEY = 'survival-island.activity.v1';
const $ = (id) => document.getElementById(id);
let activity = restore();
let editingGroup = null;
let draft = [];

function restore() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (!saved || !Number.isInteger(saved.count) || saved.count < 1 || saved.count > 8 ||
        !Array.isArray(saved.groups) || saved.groups.length !== saved.count) return null;
    const validIds = new Set(ITEMS.map((item) => item.id));
    if (!saved.groups.every((group) => Array.isArray(group) && group.length <= 3 &&
        new Set(group).size === group.length && group.every((id) => validIds.has(id)))) return null;
    return saved;
  } catch { return null; }
}

function save() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(activity)); }
  catch { $('storage-status').hidden = false; }
}

function itemContent(item) {
  const image = document.createElement('img');
  image.src = `media/${encodeURIComponent(item.file)}`;
  image.alt = ''; // The adjacent label supplies the accessible name.
  const label = document.createElement('span');
  label.className = 'item-label';
  label.textContent = item.name;
  return [image, label];
}

function showGroups() {
  $('start-screen').hidden = true;
  $('groups-screen').hidden = false;
  const table = $('group-table');
  table.replaceChildren();
  table.style.setProperty('--groups', activity.count);
  activity.groups.forEach((selected, index) => {
    const column = document.createElement('section');
    column.className = 'group-column';
    column.setAttribute('aria-label', `Group ${index + 1}`);
    const button = document.createElement('button');
    button.className = 'group-name';
    button.textContent = `Group ${index + 1}`;
    button.setAttribute('aria-haspopup', 'dialog');
    button.addEventListener('click', () => openGroup(index));
    column.append(button);
    for (let row = 0; row < 3; row++) {
      const slot = document.createElement('div');
      slot.className = 'item-slot';
      const item = ITEMS.find((item) => item.id === selected[row]);
      if (item) slot.append(...itemContent(item));
      else {
        const mark = document.createElement('span');
        mark.className = 'empty-mark';
        mark.setAttribute('aria-hidden', 'true');
        slot.setAttribute('aria-label', 'Empty item space');
        slot.append(mark);
      }
      column.append(slot);
    }
    table.append(column);
  });
}

function openGroup(index) {
  editingGroup = index;
  draft = [...activity.groups[index]];
  $('dialog-title').textContent = `GROUP ${index + 1}`;
  $('item-grid').replaceChildren();
  ITEMS.forEach((item) => {
    const button = document.createElement('button');
    button.className = 'item-choice';
    button.dataset.id = item.id;
    button.append(...itemContent(item));
    const mark = document.createElement('span');
    mark.className = 'selection-mark';
    mark.setAttribute('aria-hidden', 'true');
    button.append(mark);
    button.addEventListener('click', () => {
      if (draft.includes(item.id)) draft = draft.filter((id) => id !== item.id);
      else if (draft.length < 3) draft.push(item.id);
      updateChoices();
    });
    $('item-grid').append(button);
  });
  updateChoices();
  $('item-dialog').showModal();
}

function updateChoices() {
  $('selection-count').textContent = `${draft.length}/3`;
  document.querySelectorAll('.item-choice').forEach((button) => {
    const order = draft.indexOf(button.dataset.id);
    button.setAttribute('aria-pressed', String(order !== -1));
    button.disabled = draft.length === 3 && order === -1;
    button.querySelector('.selection-mark').hidden = order === -1;
    button.querySelector('.selection-mark').textContent = order + 1;
  });
}

$('start').addEventListener('click', () => {
  if (activity && !window.confirm('Start a new activity? The current activity will be cleared.')) return;
  const count = Number($('group-count').value);
  activity = { count, groups: Array.from({ length: count }, () => []) };
  save();
  showGroups();
  document.querySelector('.group-name').focus();
});
$('continue').addEventListener('click', () => { showGroups(); document.querySelector('.group-name').focus(); });
$('back').addEventListener('click', () => {
  $('groups-screen').hidden = true;
  $('start-screen').hidden = false;
  $('continue').hidden = !activity;
  $('group-count').value = activity.count;
  $('continue').focus();
});
$('close-dialog').addEventListener('click', () => $('item-dialog').close());
$('confirm').addEventListener('click', () => {
  const index = editingGroup;
  activity.groups[index] = [...draft];
  save();
  $('item-dialog').close();
  showGroups();
  document.querySelectorAll('.group-name')[index].focus();
});
$('item-dialog').addEventListener('close', () => { draft = []; editingGroup = null; });
if (activity) {
  $('group-count').value = activity.count;
  showGroups();
}
