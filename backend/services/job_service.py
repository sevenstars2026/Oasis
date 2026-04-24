"""工作系统服务层"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from models import Job, WorkSession, Player, PlayerState, Inventory
from utils.exceptions import GameException


class JobService:
    """工作管理服务"""

    @staticmethod
    def get_available_jobs(
        db: Session,
        location_id: Optional[int] = None,
        job_class: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Job]:
        """获取可用工作列表"""
        query = db.query(Job).filter(Job.is_available == True)

        if location_id:
            query = query.filter(Job.location_id == location_id)

        if job_class:
            query = query.filter(Job.required_job_class == job_class)

        # 只显示还有空位的工作
        query = query.filter(Job.current_workers < Job.max_workers)

        return query.order_by(Job.base_pay.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_job_by_id(db: Session, job_id: int) -> Optional[Job]:
        """根据ID获取工作"""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def start_work(db: Session, player_id: int, job_id: int) -> WorkSession:
        """开始工作"""
        # 验证工作存在
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise GameException(code=404, message="工作不存在")

        if not job.is_available:
            raise GameException(code=400, message="该工作当前不可用")

        if job.current_workers >= job.max_workers:
            raise GameException(code=400, message="该工作已满员")

        # 验证玩家
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(code=404, message="玩家不存在")

        # 验证职业匹配
        if job.required_job_class and player.job != job.required_job_class:
            raise GameException(code=403, message=f"该工作需要 {job.required_job_class} 职业")

        # 检查玩家是否已经在工作
        active_session = db.query(WorkSession).filter(
            WorkSession.player_id == player_id,
            WorkSession.status == "active"
        ).first()

        if active_session:
            raise GameException(code=400, message="你已经在工作中，请先结束当前工作")

        # 验证玩家位置（如果工作有位置要求）
        if job.location_id:
            player_state = db.query(PlayerState).filter(PlayerState.player_id == player_id).first()
            if not player_state or player_state.location_id != job.location_id:
                raise GameException(code=400, message="你不在该工作所在位置")

        # 创建工作会话
        work_session = WorkSession(
            player_id=player_id,
            job_id=job_id,
            start_time=datetime.now(),
            status="active"
        )

        # 更新工作的当前工人数
        job.current_workers += 1

        # 更新玩家状态
        player_state = db.query(PlayerState).filter(PlayerState.player_id == player_id).first()
        if player_state:
            player_state.current_activity = "working"
            player_state.current_job_id = job_id
            player_state.work_session_id = work_session.id

        db.add(work_session)
        db.commit()
        db.refresh(work_session)

        return work_session

    @staticmethod
    def end_work(db: Session, player_id: int, work_session_id: int) -> Dict:
        """结束工作并结算"""
        work_session = db.query(WorkSession).filter(
            WorkSession.id == work_session_id,
            WorkSession.player_id == player_id
        ).first()

        if not work_session:
            raise GameException(code=404, message="工作会话不存在")

        if work_session.status != "active":
            raise GameException(code=400, message="该工作会话已结束")

        # 计算工作时长
        work_session.end_time = datetime.now()
        duration = (work_session.end_time - work_session.start_time).total_seconds() / 60  # 分钟
        work_session.duration_minutes = int(duration)

        # 获取工作信息
        job = db.query(Job).filter(Job.id == work_session.job_id).first()
        if not job:
            raise GameException(code=404, message="工作不存在")

        # 计算收益（每小时工资）
        hours_worked = duration / 60
        base_earnings = job.base_pay * hours_worked

        # 应用奖金条件（简化版，后续可扩展）
        bonus_multiplier = 1.0
        if job.bonus_conditions:
            try:
                bonus_data = json.loads(job.bonus_conditions)
                # 这里可以根据玩家表现计算奖金
                # 暂时使用固定的效率奖金
                bonus_multiplier = bonus_data.get("efficiency", 1.0)
            except:
                pass

        total_earnings = base_earnings * bonus_multiplier
        work_session.earnings = total_earnings

        # 生成产出物品（根据工作类型）
        items_produced = JobService._generate_work_output(job.job_type, duration)
        work_session.output = json.dumps({"items": items_produced, "quality": 0.85})

        # 结算金币
        player = db.query(Player).filter(Player.id == player_id).first()
        if player:
            player.gold += total_earnings

        # 添加物品到背包
        for item in items_produced:
            JobService._add_to_inventory(db, player_id, item["name"], item["quantity"])

        # 更新工作状态
        work_session.status = "completed"
        job.current_workers = max(0, job.current_workers - 1)

        # 更新玩家状态
        player_state = db.query(PlayerState).filter(PlayerState.player_id == player_id).first()
        if player_state:
            player_state.current_activity = "idle"
            player_state.current_job_id = None
            player_state.work_session_id = None

        db.commit()
        db.refresh(work_session)

        return {
            "success": True,
            "duration_minutes": work_session.duration_minutes,
            "earnings": total_earnings,
            "items_produced": items_produced,
            "total_gold": player.gold if player else 0
        }

    @staticmethod
    def get_work_history(
        db: Session,
        player_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[WorkSession]:
        """获取工作历史"""
        return db.query(WorkSession).filter(
            WorkSession.player_id == player_id
        ).order_by(WorkSession.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_work_session(db: Session, player_id: int) -> Optional[WorkSession]:
        """获取玩家当前的工作会话"""
        return db.query(WorkSession).filter(
            WorkSession.player_id == player_id,
            WorkSession.status == "active"
        ).first()

    @staticmethod
    def _generate_work_output(job_type: str, duration_minutes: float) -> List[Dict]:
        """根据工作类型生成产出物品"""
        output_rate = {
            "mining": {"item": "矿石", "rate": 2},  # 每分钟2个
            "crafting": {"item": "木板", "rate": 1.5},
            "trading": {"item": "商品", "rate": 1},
            "guarding": {"item": "安全点数", "rate": 0.5},
            "researching": {"item": "知识点", "rate": 0.3}
        }

        if job_type not in output_rate:
            return []

        config = output_rate[job_type]
        quantity = int(duration_minutes * config["rate"])

        return [{"name": config["item"], "quantity": max(1, quantity)}] if quantity > 0 else []

    @staticmethod
    def _add_to_inventory(db: Session, player_id: int, item_name: str, quantity: int):
        """添加物品到背包"""
        inventory = db.query(Inventory).filter(
            Inventory.owner_id == player_id,
            Inventory.item_name == item_name
        ).first()

        if inventory:
            inventory.quantity += quantity
            inventory.updated_at = datetime.now()
        else:
            inventory = Inventory(
                owner_id=player_id,
                item_name=item_name,
                quantity=quantity
            )
            db.add(inventory)

    @staticmethod
    def process_offline_work(db: Session):
        """处理离线工作（定时任务调用）"""
        # 查找超过8小时的活跃工作会话，自动结束
        cutoff_time = datetime.now() - timedelta(hours=8)
        long_sessions = db.query(WorkSession).filter(
            WorkSession.status == "active",
            WorkSession.start_time < cutoff_time
        ).all()

        ended_count = 0
        for session in long_sessions:
            try:
                JobService.end_work(db, session.player_id, session.id)
                ended_count += 1
            except:
                # 如果结算失败，标记为中断
                session.status = "interrupted"
                session.end_time = datetime.now()

        db.commit()
        return {"ended_sessions": ended_count}
