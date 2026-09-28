import { getCareers } from "./api.js";
import "./common.js";

const target = document.querySelector("#feature-content");
const status = document.querySelector("#feature-status");

try {
  const careers = await getCareers();
  if (!careers.length) {
    target.replaceChildren();
    status.textContent = "The catalog is empty. Run `python -m scripts.seed_data` from the project directory.";
  } else {
    const fragment = document.createDocumentFragment();
    careers.forEach((career) => {
      const item = document.createElement("article");
      item.className = "catalog-item";
      const category = document.createElement("span");
      category.className = "catalog-category";
      category.textContent = career.category;
      const title = document.createElement("h3");
      title.textContent = career.name;
      const description = document.createElement("p");
      description.textContent = career.description;
      item.append(category, title, description);
      fragment.append(item);
    });
    target.replaceChildren(fragment);
  }
} catch (error) {
  target.replaceChildren();
  status.textContent = error.message;
}