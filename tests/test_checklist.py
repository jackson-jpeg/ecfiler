"""Tests for filing checklists."""

import pytest

from ecfiler.filing.checklist import get_all_checklist_types, get_checklist


class TestGetChecklist:
    def test_motion_to_dismiss(self) -> None:
        cl = get_checklist("Motion to Dismiss")
        assert cl is not None
        assert "Motion to Dismiss" in cl.title
        assert any("12(b)" in i.text for i in cl.items)
        assert any(i.required for i in cl.items)

    def test_generic_motion(self) -> None:
        cl = get_checklist("Motion for Extension of Time")
        assert cl is not None
        assert any("memorandum" in i.text.lower() or "brief" in i.text.lower() for i in cl.items)

    def test_complaint(self) -> None:
        cl = get_checklist("Complaint")
        assert cl is not None
        assert any("civil cover sheet" in i.text.lower() for i in cl.items)
        assert any("summons" in i.text.lower() for i in cl.items)
        assert any("filing fee" in i.text.lower() for i in cl.items)

    def test_answer(self) -> None:
        cl = get_checklist("Answer")
        assert cl is not None
        assert any("claims" in i.text.lower() for i in cl.items)

    def test_reply_brief(self) -> None:
        cl = get_checklist("Reply Brief")
        assert cl is not None
        assert any("deadline" in i.text.lower() for i in cl.items)

    def test_response_opposition(self) -> None:
        cl = get_checklist("Response/Opposition to Motion")
        assert cl is not None
        assert any("deadline" in i.text.lower() for i in cl.items)

    def test_notice_of_appearance(self) -> None:
        cl = get_checklist("Notice of Appearance")
        assert cl is not None
        assert any("bar number" in i.text.lower() for i in cl.items)

    def test_petition(self) -> None:
        cl = get_checklist("Voluntary Petition")
        assert cl is not None
        assert any("creditor matrix" in i.text.lower() for i in cl.items)
        assert any("credit counseling" in i.text.lower() for i in cl.items)

    def test_no_match(self) -> None:
        cl = get_checklist("Some Obscure Filing Type")
        assert cl is None

    def test_specific_beats_generic(self) -> None:
        """'Motion to Dismiss' should get the specific checklist, not generic 'motion'."""
        specific = get_checklist("Motion to Dismiss")
        generic = get_checklist("Motion for Leave to File")
        assert specific is not None
        assert generic is not None
        # Specific should have Rule 12(b) item
        assert any("12(b)" in i.text for i in specific.items)
        assert not any("12(b)" in i.text for i in generic.items)


class TestGetAllTypes:
    def test_returns_types(self) -> None:
        types = get_all_checklist_types()
        assert len(types) >= 10
        assert "motion" in types
        assert "complaint" in types
        assert "answer" in types
        assert "appeal" in types
