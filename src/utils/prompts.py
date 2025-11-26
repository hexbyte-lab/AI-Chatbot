"""
Prompt templates and management system.
"""

from typing import Dict, List, Optional
from pathlib import Path
import yaml


class PromptTemplate:
    """Single prompt template."""

    def __init__(
        self,
        name: str,
        template: str,
        description: str = "",
        variables: List[str] = None,
        category: str = "general",
    ):
        """Initialize prompt template.

        Args:
            name: Template name/identifier
            template: Template string with {variables}
            description: Human-readable description
            variables: List of variable names
            category: Template category
        """
        self.name = name
        self.template = template
        self.description = description
        self.variables = variables or []
        self.category = category

    def format(self, **kwargs) -> str:
        """Format template with provided variables.

        Args:
            **kwargs: Variable values

        Returns:
            Formatted prompt string
        """
        return self.template.format(**kwargs)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
            "variables": self.variables,
            "category": self.category,
        }


class PromptManager:
    """Manages prompt templates."""

    DEFAULT_TEMPLATES = {
        "code_review": PromptTemplate(
            name="code_review",
            template="Review the following code for bugs, security issues, and improvements:\n\n```{language}\n{code}\n```\n\nProvide specific, actionable feedback.",
            description="Code review assistant",
            variables=["code", "language"],
            category="coding",
        ),
        "explain": PromptTemplate(
            name="explain",
            template="Explain the following concept for a {level} developer:\n\n{concept}\n\nUse clear examples and avoid jargon.",
            description="Technical concept explainer",
            variables=["concept", "level"],
            category="education",
        ),
        "summarize": PromptTemplate(
            name="summarize",
            template="Summarize the following text in {num_points} key points:\n\n{text}",
            description="Text summarization",
            variables=["text", "num_points"],
            category="general",
        ),
        "debug": PromptTemplate(
            name="debug",
            template="I'm getting the following error:\n\n```\n{error}\n```\n\nIn this code:\n\n```{language}\n{code}\n```\n\nHelp me understand and fix this error.",
            description="Debugging assistant",
            variables=["error", "code", "language"],
            category="coding",
        ),
        "optimize": PromptTemplate(
            name="optimize",
            template="Optimize the following {language} code for {goal}:\n\n```{language}\n{code}\n```\n\nExplain the optimizations you make.",
            description="Code optimization",
            variables=["code", "language", "goal"],
            category="coding",
        ),
        "test": PromptTemplate(
            name="test",
            template="Generate comprehensive unit tests for this {language} function:\n\n```{language}\n{code}\n```\n\nInclude edge cases and error handling tests.",
            description="Test generation",
            variables=["code", "language"],
            category="coding",
        ),
        "document": PromptTemplate(
            name="document",
            template="Generate clear documentation for this {language} code:\n\n```{language}\n{code}\n```\n\nInclude docstrings, parameter descriptions, and usage examples.",
            description="Documentation generator",
            variables=["code", "language"],
            category="coding",
        ),
        "translate": PromptTemplate(
            name="translate",
            template="Translate this code from {from_lang} to {to_lang}:\n\n```{from_lang}\n{code}\n```\n\nMaintain functionality and add comments explaining key differences.",
            description="Code translation between languages",
            variables=["code", "from_lang", "to_lang"],
            category="coding",
        ),
        "brainstorm": PromptTemplate(
            name="brainstorm",
            template="Help me brainstorm ideas for: {topic}\n\nProvide {num_ideas} creative, diverse ideas with brief explanations.",
            description="Creative brainstorming",
            variables=["topic", "num_ideas"],
            category="creative",
        ),
        "refactor": PromptTemplate(
            name="refactor",
            template="Refactor this {language} code to improve {aspect}:\n\n```{language}\n{code}\n```\n\nExplain each refactoring step.",
            description="Code refactoring",
            variables=["code", "language", "aspect"],
            category="coding",
        ),
    }

    def __init__(self, config_path: str = "config/prompts.yaml"):
        """Initialize prompt manager.

        Args:
            config_path: Path to prompts configuration file
        """
        self.config_path = Path(config_path)
        self.templates: Dict[str, PromptTemplate] = {}

        # Load default templates
        self.templates.update(self.DEFAULT_TEMPLATES)

        # Load custom templates from config if exists
        if self.config_path.exists():
            self._load_from_file()

    def _load_from_file(self):
        """Load templates from YAML configuration file."""
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        if not config or "prompts" not in config:
            return

        for prompt_data in config["prompts"]:
            template = PromptTemplate(
                name=prompt_data["name"],
                template=prompt_data["template"],
                description=prompt_data.get("description", ""),
                variables=prompt_data.get("variables", []),
                category=prompt_data.get("category", "custom"),
            )
            self.templates[template.name] = template

    def get(self, name: str) -> Optional[PromptTemplate]:
        """Get template by name.

        Args:
            name: Template name

        Returns:
            PromptTemplate or None
        """
        return self.templates.get(name)

    def list(self, category: str = None) -> List[PromptTemplate]:
        """List all templates, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of templates
        """
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    def get_categories(self) -> List[str]:
        """Get all unique categories.

        Returns:
            List of category names
        """
        return sorted(set(t.category for t in self.templates.values()))

    def format_prompt(self, name: str, **kwargs) -> Optional[str]:
        """Get and format a prompt template.

        Args:
            name: Template name
            **kwargs: Template variables

        Returns:
            Formatted prompt or None
        """
        template = self.get(name)
        if template:
            return template.format(**kwargs)
        return None

    def add_template(self, template: PromptTemplate):
        """Add a new template.

        Args:
            template: PromptTemplate instance
        """
        self.templates[template.name] = template

    def remove_template(self, name: str) -> bool:
        """Remove a template.

        Args:
            name: Template name

        Returns:
            True if removed, False if not found
        """
        if name in self.templates:
            del self.templates[name]
            return True
        return False

    def save_to_file(self, filepath: str = None):
        """Save custom templates to file.

        Args:
            filepath: Output file path (uses config_path if None)
        """
        filepath = Path(filepath or self.config_path)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Only save non-default templates
        custom_templates = [
            t.to_dict()
            for name, t in self.templates.items()
            if name not in self.DEFAULT_TEMPLATES
        ]

        config = {"prompts": custom_templates}

        with open(filepath, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def get_template_info(self, name: str) -> Optional[Dict]:
        """Get template information.

        Args:
            name: Template name

        Returns:
            Template info dictionary or None
        """
        template = self.get(name)
        if template:
            return template.to_dict()
        return None
