export function getBulkSelectionState(itemIds, completedIds) {
  const ids = [...new Set(itemIds)];
  const completed = completedIds instanceof Set ? completedIds : new Set(completedIds);
  const completedCount = ids.filter((id) => completed.has(id)).length;

  return {
    total: ids.length,
    completedCount,
    isAllComplete: ids.length > 0 && completedCount === ids.length,
    isPartial: completedCount > 0 && completedCount < ids.length,
  };
}

export function toggleBulkSelection(itemIds, completedIds) {
  const ids = [...new Set(itemIds)];
  const nextCompleted = new Set(completedIds);
  const selection = getBulkSelectionState(ids, nextCompleted);
  const complete = !selection.isAllComplete;

  ids.forEach((id) => {
    if (complete) {
      nextCompleted.add(id);
    } else {
      nextCompleted.delete(id);
    }
  });

  return {
    complete,
    completed: nextCompleted,
  };
}
