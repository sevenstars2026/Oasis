"""
种子数据初始化脚本
用于创建初始的地图位置、工作、房产等数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from utils.database import SessionLocal, init_db
from models import Location, Job, Property, Resource
import json


def create_locations(db: Session):
    """创建初始地图位置"""
    locations = [
        {
            "name": "plaza",
            "display_name": "中央广场",
            "x": 0,
            "y": 0,
            "zone_type": "commercial",
            "description": "城市的中心，所有冒险的起点",
            "capacity": 100,
            "is_unlocked": True
        },
        {
            "name": "residential_district",
            "display_name": "住宅区",
            "x": -100,
            "y": 50,
            "zone_type": "residential",
            "description": "安静的居住区域，可以购买房产",
            "capacity": 50,
            "is_unlocked": True
        },
        {
            "name": "industrial_zone",
            "display_name": "工业区",
            "x": 100,
            "y": 50,
            "zone_type": "industrial",
            "description": "工厂和作坊聚集地，有大量工作机会",
            "capacity": 80,
            "is_unlocked": True
        },
        {
            "name": "market_street",
            "display_name": "市场街",
            "x": 0,
            "y": -100,
            "zone_type": "commercial",
            "description": "繁华的商业街，交易的好地方",
            "capacity": 60,
            "is_unlocked": True
        },
        {
            "name": "forest",
            "display_name": "森林",
            "x": -150,
            "y": -150,
            "zone_type": "wilderness",
            "description": "茂密的森林，可以采集木材和草药",
            "capacity": 30,
            "is_unlocked": True
        },
        {
            "name": "mine",
            "display_name": "矿山",
            "x": 150,
            "y": -150,
            "zone_type": "wilderness",
            "description": "丰富的矿藏，可以挖掘矿石",
            "capacity": 40,
            "is_unlocked": True
        },
        {
            "name": "harbor",
            "display_name": "港口",
            "x": 0,
            "y": 150,
            "zone_type": "commercial",
            "description": "繁忙的港口，连接外部世界",
            "capacity": 50,
            "is_unlocked": False,
            "unlock_requirement": json.dumps({"gold": 5000, "reputation": 100})
        }
    ]

    for loc_data in locations:
        existing = db.query(Location).filter(Location.name == loc_data["name"]).first()
        if not existing:
            location = Location(**loc_data)
            db.add(location)
            print(f"✅ 创建位置: {loc_data['display_name']}")

    db.commit()


def create_resources(db: Session):
    """创建资源点"""
    # 获取位置ID
    forest = db.query(Location).filter(Location.name == "forest").first()
    mine = db.query(Location).filter(Location.name == "mine").first()

    if not forest or not mine:
        print("⚠️  位置不存在，跳过资源创建")
        return

    resources = [
        {
            "location_id": forest.id,
            "resource_type": "wood",
            "amount": 1000,
            "max_amount": 1000,
            "regeneration_rate": 50,
            "difficulty": 1.0
        },
        {
            "location_id": forest.id,
            "resource_type": "herbs",
            "amount": 500,
            "max_amount": 500,
            "regeneration_rate": 30,
            "difficulty": 1.2
        },
        {
            "location_id": mine.id,
            "resource_type": "iron_ore",
            "amount": 800,
            "max_amount": 800,
            "regeneration_rate": 40,
            "difficulty": 1.5
        },
        {
            "location_id": mine.id,
            "resource_type": "stone",
            "amount": 1500,
            "max_amount": 1500,
            "regeneration_rate": 60,
            "difficulty": 0.8
        }
    ]

    for res_data in resources:
        existing = db.query(Resource).filter(
            Resource.location_id == res_data["location_id"],
            Resource.resource_type == res_data["resource_type"]
        ).first()

        if not existing:
            resource = Resource(**res_data)
            db.add(resource)
            print(f"✅ 创建资源: {res_data['resource_type']} @ Location {res_data['location_id']}")

    db.commit()


def create_jobs(db: Session):
    """创建初始工作"""
    # 获取位置ID
    industrial = db.query(Location).filter(Location.name == "industrial_zone").first()
    market = db.query(Location).filter(Location.name == "market_street").first()
    forest = db.query(Location).filter(Location.name == "forest").first()
    mine = db.query(Location).filter(Location.name == "mine").first()

    jobs = [
        {
            "title": "木材加工",
            "description": "将原木加工成木板",
            "job_type": "crafting",
            "required_job_class": "crafter",
            "required_level": 1,
            "location_id": industrial.id if industrial else None,
            "base_pay": 50,
            "bonus_conditions": json.dumps({"efficiency": 1.2}),
            "max_workers": 5,
            "employer_type": "system"
        },
        {
            "title": "矿石冶炼",
            "description": "将矿石冶炼成金属锭",
            "job_type": "crafting",
            "required_job_class": "crafter",
            "required_level": 1,
            "location_id": industrial.id if industrial else None,
            "base_pay": 60,
            "bonus_conditions": json.dumps({"efficiency": 1.3}),
            "max_workers": 4,
            "employer_type": "system"
        },
        {
            "title": "市场摊贩",
            "description": "在市场摆摊售卖商品",
            "job_type": "trading",
            "required_job_class": "merchant",
            "required_level": 1,
            "location_id": market.id if market else None,
            "base_pay": 40,
            "bonus_conditions": json.dumps({"efficiency": 1.5}),
            "max_workers": 10,
            "employer_type": "system"
        },
        {
            "title": "伐木工",
            "description": "在森林中砍伐木材",
            "job_type": "mining",
            "required_job_class": "warrior",
            "required_level": 1,
            "location_id": forest.id if forest else None,
            "base_pay": 45,
            "bonus_conditions": json.dumps({"efficiency": 1.1}),
            "max_workers": 6,
            "employer_type": "system"
        },
        {
            "title": "矿工",
            "description": "在矿山中挖掘矿石",
            "job_type": "mining",
            "required_job_class": "warrior",
            "required_level": 1,
            "location_id": mine.id if mine else None,
            "base_pay": 55,
            "bonus_conditions": json.dumps({"efficiency": 1.2}),
            "max_workers": 8,
            "employer_type": "system"
        },
        {
            "title": "图书管理员",
            "description": "整理和研究古老的知识",
            "job_type": "researching",
            "required_job_class": "scholar",
            "required_level": 1,
            "location_id": industrial.id if industrial else None,
            "base_pay": 35,
            "bonus_conditions": json.dumps({"efficiency": 1.0}),
            "max_workers": 3,
            "employer_type": "system"
        }
    ]

    for job_data in jobs:
        existing = db.query(Job).filter(Job.title == job_data["title"]).first()
        if not existing:
            job = Job(**job_data)
            db.add(job)
            print(f"✅ 创建工作: {job_data['title']}")

    db.commit()


def create_properties(db: Session):
    """创建初始房产"""
    residential = db.query(Location).filter(Location.name == "residential_district").first()
    market = db.query(Location).filter(Location.name == "market_street").first()

    if not residential or not market:
        print("⚠️  位置不存在，跳过房产创建")
        return

    properties = [
        # 住宅区房产
        {"location_id": residential.id, "property_type": "apartment", "size": 30, "current_value": 3000},
        {"location_id": residential.id, "property_type": "apartment", "size": 35, "current_value": 3500},
        {"location_id": residential.id, "property_type": "apartment", "size": 40, "current_value": 4000},
        {"location_id": residential.id, "property_type": "house", "size": 80, "current_value": 15000},
        {"location_id": residential.id, "property_type": "house", "size": 100, "current_value": 20000},
        {"location_id": residential.id, "property_type": "house", "size": 120, "current_value": 25000},

        # 市场街商铺
        {"location_id": market.id, "property_type": "shop", "size": 50, "current_value": 40000},
        {"location_id": market.id, "property_type": "shop", "size": 60, "current_value": 50000},
        {"location_id": market.id, "property_type": "warehouse", "size": 200, "current_value": 80000},
    ]

    for prop_data in properties:
        property = Property(**prop_data)
        db.add(property)

    db.commit()
    print(f"✅ 创建 {len(properties)} 个房产")


def main():
    """主函数"""
    print("🌱 开始初始化种子数据...")

    # 初始化数据库
    init_db()

    # 创建数据库会话
    db = SessionLocal()

    try:
        create_locations(db)
        create_resources(db)
        create_jobs(db)
        create_properties(db)

        print("\n✅ 种子数据初始化完成！")
        print("\n📊 数据统计:")
        print(f"  - 位置: {db.query(Location).count()} 个")
        print(f"  - 资源点: {db.query(Resource).count()} 个")
        print(f"  - 工作: {db.query(Job).count()} 个")
        print(f"  - 房产: {db.query(Property).count()} 个")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
