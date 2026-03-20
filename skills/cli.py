"""
Skills CLI Integration

Provides command-line interface integration for the skills system
Works with the main cmd.py command runner

Usage:
    python -m skills.cli list
    python -m skills.cli search "python"
    python -m skills.cli show skill-creator
    python -m skills.cli content skill-creator SKILL.md
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from skills import SkillsManager, Skill, get_skills_manager


def cmd_list(args):
    """List all available skills"""
    manager = get_skills_manager()
    skills = manager.list_skills()
    
    if args.category:
        # Filter by category prefix
        skills = [s for s in skills if s.startswith(args.category + "-")]
    
    print(f"Found {len(skills)} skills:\n")
    for skill_name in skills:
        print(f"  - {skill_name}")
    
    return 0


def cmd_search(args):
    """Search for skills"""
    manager = get_skills_manager()
    results = manager.search_skills(args.query)
    
    print(f"Found {len(results)} matching skills:\n")
    for skill in results:
        desc = skill.description[:60] + "..." if len(skill.description) > 60 else skill.description
        print(f"  - {skill.name}")
        if desc:
            print(f"    {desc}")
        print()
    
    return 0


def cmd_show(args):
    """Show details about a skill"""
    manager = get_skills_manager()
    skill = manager.get_skill(args.skill)
    
    if not skill:
        print(f"Skill not found: {args.skill}")
        return 1
    
    print(f"Skill: {skill.name}")
    print(f"Path: {skill.path}")
    print(f"Description: {skill.description}")
    print(f"\nFiles:")
    print(f"  - SKILL.md: {'✓' if skill.has_skill_md else '✗'}")
    print(f"  - README.md: {'✓' if skill.has_readme else '✗'}")
    print(f"  - scripts/: {'✓' if skill.has_scripts else '✗'}")
    print(f"  - references/: {'✓' if skill.has_references else '✗'}")
    
    # Show available files
    files = manager.get_skill_files(args.skill)
    if files:
        print(f"\nAll files:")
        for file_type, file_path in sorted(files.items()):
            print(f"  - {file_type}")
    
    return 0


def cmd_content(args):
    """Show content of a skill file"""
    manager = get_skills_manager()
    content = manager.get_skill_content(args.skill, args.file)
    
    if content is None:
        print(f"File not found: {args.file} in skill {args.skill}")
        return 1
    
    print(content)
    return 0


def cmd_categories(args):
    """List all skill categories"""
    manager = get_skills_manager()
    categories = manager.get_all_categories()
    
    print(f"Found {len(categories)} categories:\n")
    for cat in categories:
        # Count skills in this category
        count = len([s for s in manager.list_skills() if s.startswith(cat + "-")])
        print(f"  - {cat} ({count} skills)")
    
    return 0


def cmd_skills_in_category(args):
    """List skills in a specific category"""
    manager = get_skills_manager()
    skills = manager.get_skills_by_category(args.category)
    
    if not skills:
        print(f"No skills found in category: {args.category}")
        return 1
    
    print(f"Skills in '{args.category}' ({len(skills)} total):\n")
    for skill in skills:
        desc = skill.description[:60] + "..." if len(skill.description) > 60 else skill.description
        print(f"  - {skill.name}")
        if desc:
            print(f"    {desc}")
    
    return 0


def cmd_reload(args):
    """Reload skills from disk"""
    manager = get_skills_manager()
    manager.reload()
    skills = manager.list_skills()
    print(f"Reloaded {len(skills)} skills")
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Skills Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  skills list                          # List all skills
  skills list --category python       # List python skills
  skills search python                 # Search for python skills
  skills show skill-creator            # Show skill details
  skills content skill-creator         # Show SKILL.md content
  skills content skill-creator README  # Show README.md content
  skills categories                   # List all categories
  skills in-category python            # List python-* skills
  skills reload                        # Reload skills from disk
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List all skills")
    list_parser.add_argument("--category", "-c", help="Filter by category prefix")
    
    # search command
    search_parser = subparsers.add_parser("search", help="Search skills")
    search_parser.add_argument("query", help="Search query")
    
    # show command
    show_parser = subparsers.add_parser("show", help="Show skill details")
    show_parser.add_argument("skill", help="Skill name")
    
    # content command
    content_parser = subparsers.add_parser("content", help="Show skill file content")
    content_parser.add_argument("skill", help="Skill name")
    content_parser.add_argument("file", nargs="?", default="SKILL.md", help="File to show (default: SKILL.md)")
    
    # categories command
    cat_parser = subparsers.add_parser("categories", help="List all categories")
    
    # in-category command
    in_cat_parser = subparsers.add_parser("in-category", help="List skills in category")
    in_cat_parser.add_argument("category", help="Category name")
    
    # reload command
    reload_parser = subparsers.add_parser("reload", help="Reload skills from disk")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate command
    commands = {
        "list": cmd_list,
        "search": cmd_search,
        "show": cmd_show,
        "content": cmd_content,
        "categories": cmd_categories,
        "in-category": cmd_skills_in_category,
        "reload": cmd_reload,
    }
    
    if args.command in commands:
        try:
            return commands[args.command](args)
        except Exception as e:
            print(f"Error: {e}")
            return 1
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
