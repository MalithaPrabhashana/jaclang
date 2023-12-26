"""Jac Language Features."""
from __future__ import annotations

from typing import Any, Callable, Optional, Type

from jaclang.plugin.default import JacFeatureDefaults
from jaclang.plugin.spec import (
    Architype,
    EdgeDir,
    JacFeatureSpec,
    Root,
    T,
)


import pluggy


class JacFeature:
    """Jac Feature."""

    from jaclang.plugin.spec import DSFunc

    pm = pluggy.PluginManager("jac")
    pm.add_hookspecs(JacFeatureSpec)
    pm.register(JacFeatureDefaults)

    RootType: Type[Root] = Root
    EdgeDir: Type[EdgeDir] = EdgeDir

    @staticmethod
    def make_architype(
        arch_type: str, on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a new architype."""
        return JacFeature.pm.hook.make_architype(
            arch_type=arch_type, on_entry=on_entry, on_exit=on_exit
        )

    @staticmethod
    def elvis(op1: Optional[T], op2: T) -> T:
        """Jac's elvis operator feature."""
        return JacFeature.pm.hook.elvis(op1=op1, op2=op2)

    @staticmethod
    def report(expr: Any) -> Any:  # noqa: ANN401
        """Jac's report stmt feature."""
        return JacFeature.pm.hook.report(expr=expr)

    @staticmethod
    def ignore(walker: Any, expr: Any) -> bool:  # noqa: ANN401
        """Jac's ignore stmt feature."""
        return JacFeature.pm.hook.ignore(walker=walker, expr=expr)

    @staticmethod
    def visit_node(walker: Any, expr: Any) -> bool:  # noqa: ANN401
        """Jac's visit stmt feature."""
        return JacFeature.pm.hook.visit_node(walker=walker, expr=expr)

    @staticmethod
    def disengage(walker: Any) -> bool:  # noqa: ANN401
        """Jac's disengage stmt feature."""
        return JacFeature.pm.hook.disengage(walker=walker)

    @staticmethod
    def edge_ref(
        node_obj: Any,  # noqa: ANN401
        dir: EdgeDir,
        filter_type: Optional[type],
    ) -> list[Any]:  # noqa: ANN401
        """Jac's apply_dir stmt feature."""
        return JacFeature.pm.hook.edge_ref(
            node_obj=node_obj, dir=dir, filter_type=filter_type
        )

    @staticmethod
    def connect(
        left: Architype | list[Architype],
        right: Architype | list[Architype],
        edge_spec: Architype,
    ) -> Architype | list[Architype]:
        """Jac's connect operator feature.

        Note: connect needs to call assign compr with tuple in op
        """
        return JacFeature.pm.hook.connect(left=left, right=right, edge_spec=edge_spec)

    @staticmethod
    def disconnect(op1: Optional[T], op2: T, op: Any) -> T:  # noqa: ANN401
        """Jac's connect operator feature."""
        return JacFeature.pm.hook.disconnect(op1=op1, op2=op2, op=op)

    @staticmethod
    def assign_compr(
        target: list[T], attr_val: tuple[tuple[str], tuple[Any]]
    ) -> list[T]:
        """Jac's assign comprehension feature."""
        return JacFeature.pm.hook.assign_compr(target=target, attr_val=attr_val)

    @staticmethod
    def get_root() -> Architype:
        """Jac's assign comprehension feature."""
        return JacFeature.pm.hook.get_root()

    @staticmethod
    def build_edge(
        edge_dir: EdgeDir,
        conn_type: Optional[Type[Architype]],
        conn_assign: Optional[tuple],
    ) -> Architype:
        """Jac's root getter."""
        return JacFeature.pm.hook.build_edge(
            edge_dir=edge_dir, conn_type=conn_type, conn_assign=conn_assign
        )