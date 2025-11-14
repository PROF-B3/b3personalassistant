"""Desktop app dialogs"""

# Lazy imports to avoid PyQt6 dependency when not needed
__all__ = [
    'OnboardingWizard',
    'TutorialDialog',
    'show_onboarding_wizard',
    'show_tutorial_list'
]

def __getattr__(name):
    """Lazy import dialog classes to avoid PyQt6 dependency issues."""
    if name == 'OnboardingWizard':
        from .onboarding_wizard import OnboardingWizard
        return OnboardingWizard
    elif name == 'TutorialDialog':
        from .tutorial_dialog import TutorialDialog
        return TutorialDialog
    elif name == 'show_onboarding_wizard':
        from .onboarding_wizard import show_onboarding_wizard
        return show_onboarding_wizard
    elif name == 'show_tutorial_list':
        from .tutorial_dialog import show_tutorial_list
        return show_tutorial_list
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
