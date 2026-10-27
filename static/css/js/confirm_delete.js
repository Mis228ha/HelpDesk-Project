/*
 * Подтверждение удаления через модальное окно <dialog id="confirm-dialog">.
 * Ванильный JS, без библиотек. Отправку формы не перехватываем:
 * удаление выполняется обычным POST с csrf-токеном.
 */
(() => {
  "use strict";

  const dialog = document.getElementById("confirm-dialog");
  if (!dialog) return; // окно есть в разметке только у администратора

  const form = dialog.querySelector("form");
  const text = dialog.querySelector("[data-confirm-text]");
  const cancelButton = dialog.querySelector("[data-confirm-cancel]");

  // Делегирование: один обработчик на весь документ работает для всех кнопок
  // «Удалить» — и на странице заявки, и в карточках списка.
  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-delete-url]");
    if (!trigger) return;

    form.action = trigger.dataset.deleteUrl;
    // textContent (а не innerHTML) — название заявки не интерпретируется как HTML
    text.textContent =
      `Удалить заявку «${trigger.dataset.deleteTitle}»? Это действие нельзя отменить.`;
    dialog.showModal(); // Esc закрывает окно штатно
  });

  // Кнопка «Отмена»
  cancelButton.addEventListener("click", () => dialog.close());

  // Клик по фону: у <dialog> ::backdrop — часть самого элемента, поэтому
  // target === dialog только при клике мимо содержимого (оно целиком внутри <form>).
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
})();